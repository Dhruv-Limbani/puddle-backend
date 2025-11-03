from typing import List, Optional, Dict, Any
import os
import logging
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_embedding_input(ds: Dict[str, Any]) -> str:
    """Build the embedding input string from dataset components.

    Inputs considered: domain, topics, description, and columns (name + description).
    """
    domain = ds.get("domain") or ""
    topics = ds.get("topics") or []
    description = ds.get("description") or ds.get("title") or ""
    columns = ds.get("columns") or []

    col_texts = []
    for col in columns:
        name = col.get("name") if isinstance(col, dict) else None
        desc = col.get("description") if isinstance(col, dict) else None
        if name and desc:
            col_texts.append(f"{name} — {desc}")
        elif name:
            col_texts.append(f"{name}")

    topics_text = ", ".join(topics) if isinstance(topics, (list, tuple)) else str(topics)

    pieces = []
    if domain:
        pieces.append(f"This dataset focuses on the {domain} domain.")
    if topics_text:
        pieces.append(f"Topics include: {topics_text}.")
    if description:
        pieces.append(description)
    if col_texts:
        pieces.append("It includes columns like: " + ", ".join(col_texts))

    return " ".join(pieces).strip()


async def generate_embedding(text: str) -> List[float]:
    """Generate embedding for `text` using Google Gemini (`google-genai`) when available.

    This runs the blocking client call in a thread via `asyncio.to_thread` to avoid blocking the event loop.
    Returns a list[float] of length 1536 on success, otherwise a zero-vector fallback.
    """
    try:
        # Import the client and types from google-genai
        try:
            from google import genai
            from google.genai import types
        except Exception:
            import genai
            from genai import types

        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.debug("No GEMINI_API_KEY found; returning zero-vector")
            return [0.0] * 1536

        def sync_call():
            # Initialize client with provided API key
            client = genai.Client(api_key=api_key)
            # Use embed_content API as in the provided example
            resp = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY", output_dimensionality=1536),
            )
            # Extract vector
            try:
                return list(resp.embeddings[0].values)
            except Exception:
                # Try alternate response shapes
                if isinstance(resp, dict) and resp.get("embeddings"):
                    return list(resp["embeddings"][0]["values"])
                raise

        emb = await asyncio.to_thread(sync_call)
        return emb
    except Exception as e:
        logger.warning("Failed to generate embedding via google-genai: %s", e)
        return [0.0] * 1536
