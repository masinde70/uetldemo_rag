"""OpenAI embeddings service for RAG."""
import os
from typing import List, Optional

from openai import AsyncOpenAI

# Lazy-load client to allow startup without API key
_client: Optional[AsyncOpenAI] = None

EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
EMBED_DIMENSIONS = 1536  # text-embedding-3-small default


def _get_client() -> AsyncOpenAI:
    """Get or create the OpenAI client (lazy initialization)."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-placeholder"):
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for embeddings. "
                "Set a valid API key to use RAG features."
            )
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def get_embedding(text: str) -> List[float]:
    """
    Get embedding vector for a single text.

    Args:
        text: Text to embed

    Returns:
        Embedding vector as list of floats
    """
    client = _get_client()
    response = await client.embeddings.create(
        model=EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


async def get_embeddings(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """
    Get embedding vectors for multiple texts.

    Args:
        texts: List of texts to embed
        batch_size: Number of texts to process per API call

    Returns:
        List of embedding vectors
    """
    embeddings = []
    client = _get_client()

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = await client.embeddings.create(
            model=EMBED_MODEL,
            input=batch,
        )
        # Sort by index to maintain order
        batch_embeddings = sorted(response.data, key=lambda x: x.index)
        embeddings.extend([e.embedding for e in batch_embeddings])

    return embeddings
