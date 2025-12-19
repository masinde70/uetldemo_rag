"""Qdrant vector database service."""
import asyncio
import os
import uuid
from typing import Any, Dict, List, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse, ResponseHandlingException
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

# Build Qdrant URL from environment variables
# Supports both QDRANT_URL (full URL) and QDRANT_HOST/QDRANT_PORT (separate)
_qdrant_host = os.getenv("QDRANT_HOST", "localhost")
_qdrant_port = os.getenv("QDRANT_PORT", "6333")
QDRANT_URL = os.getenv("QDRANT_URL", f"http://{_qdrant_host}:{_qdrant_port}")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "sisuiq_chunks")
VECTOR_SIZE = 1536  # text-embedding-3-small

# Async client singleton
_client: Optional[AsyncQdrantClient] = None

async def get_client() -> AsyncQdrantClient:
    """Get or create async Qdrant client."""
    global _client
    if _client is None:
        _client = AsyncQdrantClient(url=QDRANT_URL)
    return _client


async def ensure_collection(max_retries: int = 10, retry_delay: float = 2.0) -> None:
    """
    Ensure the collection exists, create if missing.

    Called on startup to auto-create collection.
    Includes retry logic for container startup timing.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries
    """
    global _client
    
    for attempt in range(1, max_retries + 1):
        try:
            client = await get_client()
            
            # Try to get collection - will raise UnexpectedResponse if doesn't exist
            # or ResponseHandlingException if can't connect
            try:
                await client.get_collection(QDRANT_COLLECTION)
                print(f"✅ Qdrant collection '{QDRANT_COLLECTION}' exists")
                return  # Collection exists, we're done
            except UnexpectedResponse:
                # Collection doesn't exist (404), create it
                await client.create_collection(
                    collection_name=QDRANT_COLLECTION,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=Distance.COSINE,
                    ),
                )
                print(f"✅ Created Qdrant collection '{QDRANT_COLLECTION}'")
                return  # Created successfully
                
        except (ResponseHandlingException, ConnectionError, OSError) as e:
            if attempt < max_retries:
                print(f"⏳ Qdrant connection attempt {attempt}/{max_retries} failed, retrying in {retry_delay}s...")
                # Reset client to force new connection
                _client = None
                await asyncio.sleep(retry_delay)
            else:
                print(f"❌ Failed to connect to Qdrant after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            # Catch any other unexpected errors
            if attempt < max_retries:
                print(f"⏳ Qdrant attempt {attempt}/{max_retries} failed ({type(e).__name__}), retrying in {retry_delay}s...")
                _client = None
                await asyncio.sleep(retry_delay)
            else:
                print(f"❌ Failed to connect to Qdrant after {max_retries} attempts: {e}")
                raise


async def upsert_chunks(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
) -> None:
    """
    Upsert document chunks with embeddings to Qdrant.

    Args:
        chunks: List of chunk dicts with keys: chunk_id, document_id, chunk_index,
                text, source, page
        embeddings: List of embedding vectors matching chunks
    """
    client = await get_client()

    points = []
    for chunk, embedding in zip(chunks, embeddings):
        point = PointStruct(
            id=str(chunk["chunk_id"]),
            vector=embedding,
            payload={
                "document_id": str(chunk["document_id"]),
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "source": chunk.get("source", ""),
                "page": chunk.get("page"),
            },
        )
        points.append(point)

    await client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points,
    )


async def search_similar(
    query_vector: List[float],
    top_k: int = 10,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for similar chunks by vector.

    Args:
        query_vector: Query embedding vector
        top_k: Number of results to return
        filters: Optional filters dict with keys: source, type, document_id

    Returns:
        List of hits with payload and score
    """
    client = await get_client()

    # Build filter conditions
    qdrant_filter = None
    if filters:
        conditions = []
        if "source" in filters:
            conditions.append(
                FieldCondition(
                    key="source",
                    match=MatchValue(value=filters["source"]),
                )
            )
        if "document_id" in filters:
            conditions.append(
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=str(filters["document_id"])),
                )
            )
        if conditions:
            qdrant_filter = Filter(must=conditions)

    results = await client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        query_filter=qdrant_filter,
        with_payload=True,
    )

    hits = []
    for result in results:
        hits.append({
            "chunk_id": result.id,
            "score": result.score,
            "text": result.payload.get("text", ""),
            "source": result.payload.get("source", ""),
            "page": result.payload.get("page"),
            "document_id": result.payload.get("document_id"),
            "chunk_index": result.payload.get("chunk_index"),
        })

    return hits


async def delete_document_chunks(document_id: uuid.UUID) -> None:
    """
    Delete all chunks for a document.

    Args:
        document_id: UUID of the document to delete chunks for
    """
    client = await get_client()

    await client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=str(document_id)),
                )
            ]
        ),
    )


async def delete_by_document_id(document_id: uuid.UUID) -> int:
    """
    Delete all vectors for a document and return count.

    Args:
        document_id: UUID of the document

    Returns:
        Number of vectors deleted (estimated)
    """
    client = await get_client()

    # First count how many points we'll delete
    count_result = await client.count(
        collection_name=QDRANT_COLLECTION,
        count_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=str(document_id)),
                )
            ]
        ),
    )
    count = count_result.count

    # Now delete
    await client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=str(document_id)),
                )
            ]
        ),
    )

    return count


async def close_client() -> None:
    """Close Qdrant client connection."""
    global _client
    if _client:
        await _client.close()
        _client = None
