# app/utils/embedding_utils.py
from typing import List, Dict, Any
import os
import logging
import asyncio
from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_embedding_input(ds: Dict[str, Any]) -> str:
    """
    Build a text string suitable for embedding from a dataset dictionary.

    Considers:
    - domain
    - topics
    - description (fallback to title)
    - columns (name + description)
    """
    domain: str = ds.get("domain") or ""
    topics = ds.get("topics") or []
    description: str = ds.get("description") or ds.get("title") or ""
    columns = ds.get("columns") or []

    col_texts: List[str] = []
    for col in columns:
        # Accept either dicts or pydantic models
        if hasattr(col, "model_dump"):
            c = col.model_dump()
        else:
            c = dict(col) if isinstance(col, dict) else {}
        name = c.get("name", "")
        desc = c.get("description", "")
        if name and desc:
            col_texts.append(f"{name} — {desc}")
        elif name:
            col_texts.append(name)

    topics_text: str = ", ".join(topics) if isinstance(topics, (list, tuple)) else str(topics)

    pieces: List[str] = []
    if domain:
        pieces.append(f"This dataset focuses on the {domain} domain.")
    if topics_text:
        pieces.append(f"Topics include: {topics_text}.")
    if description:
        pieces.append(description)
        if description[:-1] != ".":
            pieces.append(".")
    if col_texts:
        pieces.append("It includes columns like: " + ", ".join(col_texts))

    result: str = " ".join(pieces).strip()
    logger.debug("Built embedding input: %s", result)
    return result


async def generate_embedding(
    text: str,
    model: str = "gemini-embedding-001",
    output_dim: int = 1536
) -> List[float]:
    """
    Generate embedding for the given text using Google Gemini (if configured).
    Returns a zero vector when the API key is missing or call fails.
    """
    try:

        api_key: str = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.debug("No GEMINI_API_KEY found; returning zero-vector.")
            return [0.0] * output_dim

        def sync_call() -> List[float]:
            client = genai.Client(api_key=api_key)
            resp = client.models.embed_content(
                model=model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="SEMANTIC_SIMILARITY",
                    output_dimensionality=output_dim,
                ),
            )
            # Try common response shapes
            try:
                return list(resp.embeddings[0].values)
            except Exception:
                if isinstance(resp, dict) and resp.get("embeddings"):
                    return list(resp["embeddings"][0]["values"])
                raise

        embedding: List[float] = await asyncio.to_thread(sync_call)
        return embedding

    except Exception as e:
        logger.warning("Failed to generate embedding via Google Gemini: %s", e)
        return [0.0] * output_dim


async def build_and_embed(
    ds: Dict[str, Any],
    model: str = "gemini-embedding-001",
    output_dim: int = 1536
) -> List[float]:
    """
    Convenience: build embedding input from dataset and generate embedding.
    """
    text: str = build_embedding_input(ds)
    return await generate_embedding(text, model=model, output_dim=output_dim)
