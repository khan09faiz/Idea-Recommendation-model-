import math
import time
import subprocess
import shutil
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

import numpy as np

from .config import EMBED_MODEL, EMBED_DIM, RETRIEVAL_K, ALPHA, GAMMA, OLLAMA_MODEL, PROMPT_TEMPLATE


# Lazy-loaded heavy objects
_embed_model = None
_faiss_index = None
_seed_texts = None


def _is_command_available(cmd: str) -> bool:
    if cmd == "ollama":
        # Check common Ollama installation paths
        common_paths = [
            r"C:\Users\hp\AppData\Local\Programs\Ollama\ollama.exe",
            r"C:\Program Files\Ollama\ollama.exe",
            r"C:\Program Files (x86)\Ollama\ollama.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return True
    return shutil.which(cmd) is not None


def _ensure_embed(encode_texts=None):
    global _embed_model, _seed_texts
    if _embed_model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _embed_model = SentenceTransformer(EMBED_MODEL)
        except Exception:
            # Fallback: provide a lightweight deterministic embedder using numpy
            class DummyEmbed:
                def __init__(self, dim=EMBED_DIM):
                    self.dim = dim

                def encode(self, texts, normalize_embeddings=True):
                    # deterministic vectors: based on text length
                    out = []
                    for i, t in enumerate(texts):
                        v = np.ones(self.dim, dtype="float32") * ((len(t) % 10) + 1)
                        if normalize_embeddings:
                            norm = np.linalg.norm(v)
                            if norm > 0:
                                v = v / norm
                        out.append(v)
                    return np.stack(out)

            _embed_model = DummyEmbed()
    if encode_texts is not None:
        _seed_texts = encode_texts
    return _embed_model


def metadata_boost(idea: Dict[str, Any], user_tags: List[str]) -> float:
    """
    Calculate metadata boost score for better ranking.
    Considers popularity, recency, tag matching, and content quality.
    """
    score = 0.0
    
    # 1. Popularity boost (normalized)
    pop = min(idea.get("popularity", 0) / 100, 1.0)
    score += pop * 0.3
    
    # 2. Recency boost (more recent ideas get higher scores)
    try:
        created = datetime.fromisoformat(str(idea.get("created_at", "2025-01-01")))
        days = (datetime.utcnow() - created).days
        recency = 1.0 / (1.0 + math.log10(max(days, 1) + 1))
        score += recency * 0.2
    except:
        score += 0.1  # Default for invalid dates
    
    # 3. Tag matching boost (significant impact)
    if user_tags:
        idea_tags = [tag.lower().strip() for tag in idea.get("tags", [])]
        user_tags_lower = [tag.lower().strip() for tag in user_tags]
        
        exact_matches = sum(1 for tag in user_tags_lower if tag in idea_tags)
        partial_matches = sum(1 for user_tag in user_tags_lower 
                            for idea_tag in idea_tags 
                            if user_tag in idea_tag or idea_tag in user_tag)
        
        tag_score = (exact_matches * 2 + partial_matches) / (len(user_tags_lower) * 2)
        score += min(tag_score, 1.0) * 0.4
    
    # 4. Content quality boost
    title_len = len(idea.get("title", ""))
    desc_len = len(idea.get("description", ""))
    
    if title_len >= 20 and desc_len >= 80:  # High quality content
        score += 0.1
    elif title_len >= 10 and desc_len >= 50:  # Good quality content
        score += 0.05
    
    return min(score, 1.0)  # Cap at 1.0


def build_embedding_index(seed_texts: List[str]):
    global _faiss_index
    embed = _ensure_embed()
    vecs = embed.encode(seed_texts, normalize_embeddings=True).astype("float32")
    try:
        import faiss

        idx = faiss.IndexFlatIP(EMBED_DIM)
        idx.add(vecs)
        _faiss_index = idx
    except Exception:
        # fall back to numpy brute-force
        _faiss_index = (vecs, seed_texts)
    return _faiss_index


def has_index() -> bool:
    return _faiss_index is not None


def retrieve_candidates(query: str, top_n: int = RETRIEVAL_K):
    embed = _ensure_embed()
    qv = embed.encode([query], normalize_embeddings=True).astype("float32")
    idx = _faiss_index
    if idx is None:
        raise RuntimeError("Embedding index not built")
    if isinstance(idx, tuple):
        vecs, _ = idx
        sims = (vecs @ qv.T).reshape(-1)
        order = np.argsort(-sims)[:top_n]
        # return (sim, idx) pairs
        return [(float(sims[i]), int(i)) for i in order]
    else:
        sims, idxs = idx.search(qv, top_n)
        return [(float(sims[0][i]), int(idxs[0][i])) for i in range(len(idxs[0]))]


def ollama_generate(query: str, seeds: List[str], user_tags: List[str] = None, n: int = 5) -> str:
    # Check if ollama CLI is present; if not, skip generation
    if not _is_command_available("ollama"):
        raise RuntimeError("Ollama CLI not found; generation disabled in this environment")
    
    user_tags = user_tags or []
    user_tags_str = ", ".join(user_tags) if user_tags else "general"
    
    prompt = PROMPT_TEMPLATE.format(
        query=query, 
        seeds=" | ".join(seeds[:3]), 
        user_tags=user_tags_str,
        n=n
    )
    
    # Use full path to ollama.exe if available
    ollama_cmd = "ollama"
    ollama_path = r"C:\Users\hp\AppData\Local\Programs\Ollama\ollama.exe"
    if os.path.exists(ollama_path):
        ollama_cmd = ollama_path
    
    result = subprocess.run([
        ollama_cmd,
        "run",
        OLLAMA_MODEL,
    ], input=prompt.encode("utf-8"), capture_output=True)
    return result.stdout.decode("utf-8")


def fallback_generate(query: str, user_tags: List[str] = None, n: int = 3) -> str:
    """
    Generate ideas using rule-based approach when Ollama is not available.
    Creates highly targeted ideas based on query keywords and user tags.
    """
    user_tags = user_tags or []
    query_lower = query.lower()
    user_tags_lower = [tag.lower().strip() for tag in user_tags]
    
    ideas = []
    
    # Analyze query for intent and context
    is_money_focused = any(word in query_lower for word in ["money", "revenue", "profit", "income", "earn", "generate", "business"])
    is_health_focused = any(word in query_lower for word in ["health", "medical", "healthcare", "wellness", "elderly", "care"])
    is_tech_focused = any(word in query_lower for word in ["ai", "tech", "digital", "smart", "automated", "platform"])
    is_current_market = any(word in query_lower for word in ["current", "market", "trend", "emerging", "new"])
    
    # Generate ideas based on specific tag combinations and query intent
    if "blockchain" in user_tags_lower:
        if "logistics" in user_tags_lower and is_money_focused:
            ideas.append({
                "title": "Blockchain Freight Tracking Revenue Platform",
                "description": "End-to-end freight tracking using blockchain smart contracts with automated payments and dispute resolution, generating revenue through transaction fees and premium analytics for shippers.",
                "tags": ["blockchain", "logistics", "freight", "revenue"]
            })
            
        if "health" in user_tags_lower or "healthcare" in user_tags_lower:
            ideas.append({
                "title": "Blockchain Medical Records Monetization",
                "description": "Secure patient data sharing platform where patients control and monetize their anonymized health data for research, earning passive income while advancing medical science.",
                "tags": ["blockchain", "healthcare", "data-monetization", "privacy"]
            })
    
    if "logistics" in user_tags_lower:
        if is_money_focused:
            ideas.append({
                "title": "Smart Logistics Capacity Marketplace",
                "description": "AI-powered platform matching unused logistics capacity with shippers in real-time, creating revenue streams for logistics providers through dynamic pricing and optimization.",
                "tags": ["logistics", "ai", "marketplace", "optimization"]
            })
            
        if "ai" in user_tags_lower:
            ideas.append({
                "title": "Predictive Logistics Network Optimizer",
                "description": "Machine learning system that predicts logistics disruptions and optimizes routes in real-time, monetized through SaaS subscriptions and performance-based pricing.",
                "tags": ["ai", "logistics", "prediction", "saas"]
            })
    
    if "ai" in user_tags_lower:
        if is_health_focused:
            ideas.append({
                "title": "AI Health Monitoring Revenue Stream",
                "description": "Wearable-integrated AI that monitors health metrics and provides personalized recommendations, generating revenue through health insurance partnerships and premium wellness plans.",
                "tags": ["ai", "health", "wearables", "insurance"]
            })
            
        if is_money_focused and is_current_market:
            ideas.append({
                "title": "AI-Powered Investment Insight Platform",
                "description": "Real-time market analysis AI that provides investment insights for retail investors, monetized through subscription tiers and commission partnerships with brokers.",
                "tags": ["ai", "finance", "investment", "market-analysis"]
            })
    
    if is_health_focused:
        if "elderly" in user_tags_lower:
            ideas.append({
                "title": "Elder Care Technology Revenue Model",
                "description": "Comprehensive elderly monitoring and care coordination platform with family engagement features, generating revenue through monthly subscriptions and insurance billing.",
                "tags": ["healthcare", "elderly", "monitoring", "family"]
            })
            
        if "blockchain" in user_tags_lower:
            ideas.append({
                "title": "Decentralized Health Insurance Pool",
                "description": "Community-driven health insurance model using blockchain for transparent claims processing and cost sharing, creating sustainable healthcare financing for underserved populations.",
                "tags": ["blockchain", "healthcare", "insurance", "community"]
            })
    
    # If no specific matches, create generic but relevant ideas
    if not ideas:
        if is_money_focused:
            ideas = [
                {
                    "title": f"{'AI' if 'ai' in user_tags_lower else 'Digital'} Revenue Optimization Platform",
                    "description": f"Smart platform that analyzes {' and '.join(user_tags[:2]) if user_tags else 'business'} data to identify new revenue opportunities and optimize existing income streams through automated insights and recommendations.",
                    "tags": user_tags[:2] + ["revenue", "optimization"] if user_tags else ["business", "revenue", "analytics"]
                },
                {
                    "title": f"Niche {user_tags[0].title() if user_tags else 'Business'} Marketplace",
                    "description": f"Specialized marketplace connecting {user_tags[0] if user_tags else 'business'} professionals with clients, monetized through transaction fees, premium listings, and value-added services.",
                    "tags": user_tags[:2] + ["marketplace", "services"] if user_tags else ["marketplace", "business", "services"]
                }
            ]
    
    # Ensure we have enough ideas
    while len(ideas) < n:
        ideas.append({
            "title": f"Innovative {user_tags[0].title() if user_tags else 'Tech'} Solution",
            "description": f"Cutting-edge {user_tags[0] if user_tags else 'technology'} solution that addresses current market needs with sustainable revenue models through subscriptions and partnerships.",
            "tags": user_tags[:2] + ["innovation", "revenue"] if user_tags else ["technology", "innovation", "revenue"]
        })
    
    # Format as string similar to LLM output
    formatted_ideas = []
    for i, idea in enumerate(ideas[:n], 1):
        formatted_ideas.append(f"Title: {idea['title']}\nDescription: {idea['description']}\nTags: {', '.join(idea['tags'])}")
    
    return "\n\n".join(formatted_ideas)


def mmr_diversify(candidates: List[Tuple[float, Dict]], embeddings: np.ndarray, lambda_param: float = 0.7, top_k: int = 10) -> List[Tuple[float, Dict]]:
    """
    Apply Maximal Marginal Relevance (MMR) for diversity-aware ranking.
    
    Args:
        candidates: List of (relevance_score, idea_dict) tuples
        embeddings: Embedding vectors for each candidate (same order)
        lambda_param: Balance between relevance (1.0) and diversity (0.0)
        top_k: Number of results to return
    
    Returns:
        Diversified list of (score, idea) tuples
    """
    if len(candidates) <= 1 or embeddings.shape[0] == 0:
        return candidates[:top_k]
    
    selected = []
    remaining = list(range(len(candidates)))
    
    # Start with highest scoring candidate
    best_idx = 0
    selected.append((candidates[best_idx][0], candidates[best_idx][1]))
    remaining.remove(best_idx)
    
    # Iteratively select candidates balancing relevance and diversity
    while len(selected) < top_k and remaining:
        mmr_scores = []
        
        for idx in remaining:
            relevance = candidates[idx][0]
            
            # Calculate max similarity to already selected items
            max_sim = 0.0
            if selected:
                selected_indices = [remaining.index(i) if i in remaining else 0 for i in range(len(selected))]
                for sel_idx in range(len(selected)):
                    # Use actual embedding similarity
                    sim = float(np.dot(embeddings[idx], embeddings[sel_idx]))
                    max_sim = max(max_sim, sim)
            
            # MMR score: λ * relevance - (1-λ) * max_similarity
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            mmr_scores.append((mmr_score, idx))
        
        # Select candidate with highest MMR score
        mmr_scores.sort(reverse=True)
        best_mmr_idx = mmr_scores[0][1]
        selected.append((candidates[best_mmr_idx][0], candidates[best_mmr_idx][1]))
        remaining.remove(best_mmr_idx)
    
    return selected


def safe_parse_llm(text: str) -> List[Dict[str, Any]]:
    ideas, cur = [], {"title": "", "description": "", "tags": []}
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.lower().startswith("title:"):
            if cur["title"]:
                ideas.append(cur)
                cur = {"title": "", "description": "", "tags": []}
            cur["title"] = s.split(":", 1)[1].strip()
        elif s.lower().startswith("description:"):
            cur["description"] = s.split(":", 1)[1].strip()
        elif s.lower().startswith("tags:"):
            cur["tags"] = [t.strip() for t in s.split(":", 1)[1].split(",")]
    if cur.get("title"):
        ideas.append(cur)
    for i, idea in enumerate(ideas):
        idea["id"] = f"G{int(time.time())}{i:02d}"
    return ideas


def is_idea_relevant(idea: dict, query: str, user_tags: List[str], min_score: float = 0.3) -> bool:
    """
    Check if an idea is truly relevant to the user's query and tags.
    """
    query_lower = query.lower()
    idea_title = idea.get("title", "").lower()
    idea_desc = idea.get("description", "").lower()
    idea_tags = [tag.lower() for tag in idea.get("tags", [])]

    relevance_score = 0.0

    query_words = set(query_lower.split())
    title_words = set(idea_title.split())
    title_match = len(query_words.intersection(title_words)) / max(len(query_words), 1)
    relevance_score += title_match * 0.4

    desc_words = set(idea_desc.split())
    desc_match = len(query_words.intersection(desc_words)) / max(len(query_words), 1)
    relevance_score += desc_match * 0.3

    if user_tags:
        user_tags_lower = [tag.lower().strip() for tag in user_tags]
        tag_matches = 0
        for user_tag in user_tags_lower:
            for idea_tag in idea_tags:
                if user_tag in idea_tag or idea_tag in user_tag:
                    tag_matches += 1
                    break
        tag_score = tag_matches / len(user_tags_lower)
        relevance_score += tag_score * 0.3

    money_keywords = ["money", "revenue", "profit", "income", "monetize", "business", "earn"]
    if any(word in query_lower for word in money_keywords):
        if any(word in idea_desc or word in idea_title for word in money_keywords):
            relevance_score += 0.2

    tech_keywords = ["ai", "blockchain", "tech", "digital", "smart", "automated"]
    query_tech = [word for word in tech_keywords if word in query_lower]
    idea_tech = [word for word in tech_keywords if word in idea_desc or word in idea_title]
    if query_tech and idea_tech:
        tech_overlap = len(set(query_tech).intersection(set(idea_tech))) / len(query_tech)
        relevance_score += tech_overlap * 0.2

    return relevance_score >= min_score


def filter_relevant_ideas(candidates: List[tuple], query: str, user_tags: List[str]) -> List[tuple]:
    """
    Filter candidates to only include truly relevant ideas.
    """
    relevant_candidates = []
    for score, idea, source in candidates:
        if is_idea_relevant(idea, query, user_tags):
            relevant_candidates.append((score, idea, source))
        else:
            # keep quiet in tests but allow debug logging in real runs
            pass
    return relevant_candidates

