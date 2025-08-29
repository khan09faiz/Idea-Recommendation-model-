from typing import List, Optional
import logging

# Keep top-level imports light so tests can import this module without heavy
# ML dependencies.
from .config import RecommendRequest, Idea, RETRIEVAL_K
from .data_processing import load_ideas, canonicalize, save_generated_ideas
from . import utils
from .utils import is_idea_relevant, filter_relevant_ideas

logger = logging.getLogger(__name__)


# relevance helpers moved to src.utils for better modularity


def hybrid_recommend(req: RecommendRequest, k: int = RETRIEVAL_K) -> List[Idea]:
    """Core hybrid recommendation logic.

    Uses helpers in src.utils which handle lazy-loading and fallbacks.
    """
    ideas = load_ideas()

    if not utils.has_index():
        seed_texts = [canonicalize(i) for i in ideas]
        try:
            utils.build_embedding_index(seed_texts)
        except Exception as e:
            logger.debug("Failed to build embedding index: %s", e)

    candidates = utils.retrieve_candidates(req.query, top_n=max(10, k * 2))

    generated = []
    if getattr(req, "generate", False):
        try:
            seeds = [canonicalize(i) for i in ideas]
            raw = utils.ollama_generate(req.query, seeds=seeds, user_tags=req.user_tags or [], n=3)
            generated = utils.safe_parse_llm(raw)
        except RuntimeError:
            # Fallback to rule-based generation
            try:
                raw = utils.fallback_generate(req.query, getattr(req, 'user_tags', []), n=3)
                generated = utils.safe_parse_llm(raw)
                logger.info("Using fallback idea generation (Ollama not available)")
            except Exception as e:
                logger.debug("Fallback generation failed: %s", e)
                generated = []

    pool: List[tuple] = []
    for sim, idx in candidates:
        idea = ideas[idx].copy()
        pool.append((float(sim), idea, "retrieved"))

    for g in generated:
        pool.append((0.01, g, "generated"))

    # Auto-save generated ideas to idea.json for future use
    if generated:
        save_generated_ideas(generated)

    scored: List[tuple] = []
    for sim, idea, src in pool:
        boost = utils.metadata_boost(idea, req.user_tags or [])
        score = utils.ALPHA * sim + utils.GAMMA * boost
        scored.append((float(score), idea, src))

    # Filter out irrelevant ideas before ranking
    scored = filter_relevant_ideas(scored, req.query, req.user_tags or [])
    
    if not scored:
        logger.warning("No relevant ideas found for query: %s", req.query)
        return []

    scored.sort(key=lambda x: x[0], reverse=True)

    # Apply MMR diversity if requested and we have embeddings
    final_candidates = [(score, idea) for score, idea, src in scored]
    
    if getattr(req, "diversify", True) and len(final_candidates) > 1:
        try:
            # Get embeddings for all candidates for MMR
            embed = utils._ensure_embed()
            candidate_texts = [canonicalize(idea) for _, idea in final_candidates]
            embeddings = embed.encode(candidate_texts, normalize_embeddings=True)
            
            # Apply MMR diversification
            final_candidates = utils.mmr_diversify(
                final_candidates, 
                embeddings, 
                lambda_param=0.7,  # Balance relevance vs diversity
                top_k=k
            )
        except Exception as e:
            logger.debug("MMR diversification failed, using original ranking: %s", e)
            final_candidates = final_candidates[:k]
    else:
        final_candidates = final_candidates[:k]

    results: List[Idea] = []
    for score, idea in final_candidates:
        results.append(
            Idea(
                id=str(idea.get("id", "unknown")),
                title=idea.get("title", ""),
                description=idea.get("description", ""),
                tags=idea.get("tags", []),
                score=round(float(score), 4),
            )
        )

    return results


# Create FastAPI app at import time only if FastAPI is installed.
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app: Optional[FastAPI] = FastAPI(title="Creative Idea Recommender")
    
    # Enable CORS for web frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {
            "message": "Creative Idea Recommendation System", 
            "docs": "/docs",
            "recommend": "/recommend"
        }

    @app.post("/recommend", response_model=List[Idea])
    def recommend_endpoint(req: RecommendRequest):
        try:
            return hybrid_recommend(req, k=getattr(req, "k", RETRIEVAL_K))
        except Exception as exc:
            logger.exception("Recommendation failed: %s", exc)
            # Re-raise to let FastAPI turn it into a 500
            raise

except Exception:
    app = None


def create_app():
    """Create and return FastAPI app instance"""
    if app is None:
        raise RuntimeError("FastAPI is not installed in this environment")
    return app


__all__ = ["app", "create_app", "hybrid_recommend"]
