import os
from typing import List
from pydantic import BaseModel, Field

# Models used across the package
class RecommendRequest(BaseModel):
    query: str
    user_tags: List[str] = Field(default_factory=list)
    k: int = Field(default=5, ge=1, le=20)
    diversify: bool = True
    generate: bool = True


class Idea(BaseModel):
    id: str
    title: str = ""
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    score: float = 0.0
    source: str = ""
    reasoning: str = ""


# Configuration constants
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384
RETRIEVAL_K = 20
ALPHA = 0.6
GAMMA = 0.2
OLLAMA_MODEL = "llama3.2:1b"

# Prompt template for generation
PROMPT_TEMPLATE = """You are an expert product strategist and innovation consultant. Generate highly detailed, practical, and market-ready product ideas that directly address the user's specific request.

User Query: "{query}"
Required Tags: {user_tags}
Context (Related Ideas): {seeds}

CRITICAL REQUIREMENTS:
1. Ideas MUST directly solve the problem stated in the query
2. Ideas MUST incorporate ALL specified tags: {user_tags}
3. Descriptions MUST be 3-4 detailed sentences (minimum 80 words) explaining:
   - What the product/service does
   - How it addresses the user's specific needs
   - Key features and benefits
   - Target market and value proposition
4. Ideas MUST be unique from the context examples above
5. Ideas MUST be technically feasible and commercially viable
6. Include clear monetization strategy if query mentions revenue/money
7. Be specific and actionable, not generic or vague

Generate {n} innovative, detailed product ideas that strictly match all requirements.

Format each idea EXACTLY as shown:
Title: [Specific, compelling product name that reflects the query and tags]
Description: [Comprehensive 3-4 sentence description covering what it does, how it works, key benefits, and target market. Minimum 80 words. Be specific about features, technology, and value proposition.]
Tags: [Include ALL user's specified tags plus 2-3 additional relevant tags]

EXAMPLE FORMAT:
Title: AI-Powered Aesthetic Cafe Experience Platform
Description: A comprehensive digital platform that transforms traditional cafes into Instagram-worthy, Gen Z-focused destinations through smart ambient lighting, AI-curated music playlists, and interactive photo booth stations. The system analyzes customer preferences and social media trends to automatically adjust the cafe's atmosphere, lighting, and featured menu items to maximize social media engagement and customer satisfaction. Features include augmented reality menu experiences, TikTok-ready video recording spots with professional lighting, and personalized food presentation based on aesthetic preferences. Targets Gen Z customers aged 16-25 who value unique experiences, social media content creation, and aesthetic dining environments.
Tags: aesthetic, genz, love, unique, food, tiktok, social-media, experience-design, hospitality

Now generate {n} ideas following this exact format and quality standard."""

# Path helpers
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IDEA_JSON_PATH = os.path.join(ROOT_DIR, "data", "idea.json")
