"""Hybrid RAG retrieval with Reciprocal Rank Fusion."""
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Document, DocumentChunk
from backend.services.embeddings import get_embedding
from backend.services.qdrant import search_similar


async def semantic_search(
    query: str,
    top_k: int = 10,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Perform semantic search using Qdrant.

    Args:
        query: Search query text
        top_k: Number of results to return
        filters: Optional filters (source, document_id)

    Returns:
        List of ranked hits with metadata
    """
    # Get query embedding
    query_vector = await get_embedding(query)

    # Search Qdrant
    hits = await search_similar(
        query_vector=query_vector,
        top_k=top_k,
        filters=filters,
    )

    # Add rank for RRF
    for rank, hit in enumerate(hits):
        hit["rank"] = rank + 1
        hit["search_type"] = "semantic"

    return hits


async def keyword_search(
    query: str,
    db: AsyncSession,
    top_k: int = 10,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Perform keyword search using PostgreSQL Full-Text Search.

    Args:
        query: Search query text
        db: Database session
        top_k: Number of results to return
        filters: Optional filters (source, type)

    Returns:
        List of ranked hits with metadata
    """
    # Convert query to tsquery
    # Use plainto_tsquery for simple queries, websearch_to_tsquery for more complex
    tsquery = func.plainto_tsquery("english", query)

    # Build base query with FTS ranking
    stmt = (
        select(
            DocumentChunk.id,
            DocumentChunk.document_id,
            DocumentChunk.chunk_index,
            DocumentChunk.text,
            DocumentChunk.source,
            DocumentChunk.page,
            func.ts_rank(DocumentChunk.fts_vector, tsquery).label("rank_score"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.fts_vector.op("@@")(tsquery))
    )

    # Apply filters
    if filters:
        if "source" in filters:
            stmt = stmt.where(Document.source == filters["source"])
        if "type" in filters:
            stmt = stmt.where(Document.type == filters["type"])
        if "document_id" in filters:
            stmt = stmt.where(DocumentChunk.document_id == filters["document_id"])

    # Order by rank and limit
    stmt = stmt.order_by(text("rank_score DESC")).limit(top_k)

    result = await db.execute(stmt)
    rows = result.all()

    hits = []
    for rank, row in enumerate(rows):
        hits.append({
            "chunk_id": str(row.id),
            "document_id": str(row.document_id),
            "chunk_index": row.chunk_index,
            "text": row.text,
            "source": row.source or "",
            "page": row.page,
            "score": float(row.rank_score),
            "rank": rank + 1,
            "search_type": "keyword",
        })

    return hits


def rrf_fusion(
    semantic_hits: List[Dict[str, Any]],
    keyword_hits: List[Dict[str, Any]],
    k: int = 60,
) -> List[Dict[str, Any]]:
    """
    Merge ranked lists using Reciprocal Rank Fusion.

    RRF formula: score = sum(1 / (k + rank)) for each list

    Args:
        semantic_hits: Results from semantic search
        keyword_hits: Results from keyword search
        k: RRF constant (default 60, higher = more weight to lower ranks)

    Returns:
        Merged and re-ranked list of hits
    """
    # Dictionary to accumulate RRF scores by chunk_id
    scores: Dict[str, float] = {}
    chunks: Dict[str, Dict[str, Any]] = {}

    # Process semantic hits
    for hit in semantic_hits:
        chunk_id = hit["chunk_id"]
        rrf_score = 1.0 / (k + hit["rank"])
        scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score

        if chunk_id not in chunks:
            chunks[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": hit.get("document_id"),
                "chunk_index": hit.get("chunk_index"),
                "text": hit["text"],
                "source": hit["source"],
                "page": hit.get("page"),
                "semantic_rank": hit["rank"],
                "keyword_rank": None,
            }
        else:
            chunks[chunk_id]["semantic_rank"] = hit["rank"]

    # Process keyword hits
    for hit in keyword_hits:
        chunk_id = hit["chunk_id"]
        rrf_score = 1.0 / (k + hit["rank"])
        scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score

        if chunk_id not in chunks:
            chunks[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": hit.get("document_id"),
                "chunk_index": hit.get("chunk_index"),
                "text": hit["text"],
                "source": hit["source"],
                "page": hit.get("page"),
                "semantic_rank": None,
                "keyword_rank": hit["rank"],
            }
        else:
            chunks[chunk_id]["keyword_rank"] = hit["rank"]

    # Sort by RRF score (descending)
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    # Build final result list
    results = []
    for chunk_id in sorted_ids:
        chunk = chunks[chunk_id]
        chunk["rrf_score"] = scores[chunk_id]
        results.append(chunk)

    return results


async def hybrid_retrieve(
    query: str,
    db: AsyncSession,
    top_n: int = 8,
    semantic_k: int = 15,
    keyword_k: int = 15,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Perform hybrid retrieval combining semantic and keyword search with RRF.

    Args:
        query: Search query
        db: Database session
        top_n: Final number of results to return
        semantic_k: Number of semantic search results
        keyword_k: Number of keyword search results
        filters: Optional filters (source, type, document_id)

    Returns:
        Fused list of chunks with metadata
    """
    # Run both searches (could parallelize with asyncio.gather)
    semantic_hits = await semantic_search(query, top_k=semantic_k, filters=filters)
    keyword_hits = await keyword_search(query, db, top_k=keyword_k, filters=filters)

    # Fuse results
    fused = rrf_fusion(semantic_hits, keyword_hits)

    # Return top N
    results = fused[:top_n]

    # Enrich with document info if needed
    for result in results:
        # Format source citation
        page = result.get("page")
        source = result.get("source", "Unknown")
        if page:
            result["citation"] = f"[{source} p.{page}]"
        else:
            result["citation"] = f"[{source}]"

    return results


async def get_document_name(document_id: str, db: AsyncSession) -> str:
    """Get document name by ID."""
    stmt = select(Document.name).where(Document.id == document_id)
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    return row or "Unknown Document"
