"""Document lifecycle operations service.

Provides delete and reindex operations for documents with proper
cleanup of both database records and Qdrant vectors.
"""
import uuid
from pathlib import Path
from typing import Optional

from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Document, DocumentChunk
from backend.services.chunking import chunk_text
from backend.services.embeddings import get_embeddings
from backend.services.qdrant import delete_by_document_id, upsert_chunks


class DocumentNotFoundError(Exception):
    """Raised when document is not found."""
    pass


class DocumentOperationError(Exception):
    """Raised when a document operation fails."""
    pass


async def delete_document(
    db: AsyncSession,
    document_id: uuid.UUID,
    trace_id: Optional[str] = None,
) -> dict:
    """Delete a document and all associated data.
    
    Removes:
    - Document record from Postgres
    - All chunk records from Postgres (via CASCADE)
    - All vectors from Qdrant
    - Optionally the stored file (configurable)
    
    Args:
        db: Database session
        document_id: Document UUID
        trace_id: Optional trace ID for logging
        
    Returns:
        Dict with deletion summary
        
    Raises:
        DocumentNotFoundError: If document doesn't exist
    """
    log_prefix = f"[{trace_id}] " if trace_id else ""
    logger.info(f"{log_prefix}Deleting document {document_id}")
    
    # Get document to verify it exists
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise DocumentNotFoundError(f"Document {document_id} not found")
    
    # Count chunks for summary
    chunk_count_result = await db.execute(
        select(DocumentChunk.id).where(DocumentChunk.document_id == document_id)
    )
    chunk_ids = [row[0] for row in chunk_count_result.all()]
    chunks_deleted = len(chunk_ids)
    
    # Get file path before deletion
    file_path = document.file_path
    
    # Delete from Qdrant first (so we can rollback DB if this fails)
    try:
        vectors_deleted = await delete_by_document_id(document_id)
        logger.debug(f"{log_prefix}Deleted {vectors_deleted} vectors from Qdrant")
    except Exception as e:
        logger.error(f"{log_prefix}Failed to delete vectors from Qdrant: {e}")
        raise DocumentOperationError(f"Failed to delete vectors: {e}")
    
    # Delete from database (chunks cascade automatically)
    await db.delete(document)
    await db.commit()
    
    logger.info(
        f"{log_prefix}✅ Deleted document {document_id}: "
        f"{chunks_deleted} chunks, {vectors_deleted} vectors"
    )
    
    return {
        "document_id": str(document_id),
        "name": document.name,
        "chunks_deleted": chunks_deleted,
        "vectors_deleted": vectors_deleted,
        "file_path": file_path,
    }


async def reindex_document(
    db: AsyncSession,
    document_id: uuid.UUID,
    trace_id: Optional[str] = None,
) -> dict:
    """Reindex a document by re-chunking and re-embedding.
    
    Preserves the document record but regenerates all chunks
    and vectors from the stored file.
    
    Args:
        db: Database session
        document_id: Document UUID
        trace_id: Optional trace ID for logging
        
    Returns:
        Dict with reindex summary
        
    Raises:
        DocumentNotFoundError: If document doesn't exist
        DocumentOperationError: If file is missing or reindex fails
    """
    from backend.routers.ingest import extract_pdf_text, determine_page
    
    log_prefix = f"[{trace_id}] " if trace_id else ""
    logger.info(f"{log_prefix}Reindexing document {document_id}")
    
    # Get document
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise DocumentNotFoundError(f"Document {document_id} not found")
    
    # Verify file exists
    file_path = Path(document.file_path)
    # Try relative to common locations
    if not file_path.exists():
        file_path = Path("storage") / document.file_path
    if not file_path.exists():
        file_path = Path(document.file_path.replace("storage/", ""))
    if not file_path.exists():
        raise DocumentOperationError(
            f"Source file not found: {document.file_path}"
        )
    
    # Delete existing vectors from Qdrant
    try:
        vectors_deleted = await delete_by_document_id(document_id)
        logger.debug(f"{log_prefix}Deleted {vectors_deleted} old vectors")
    except Exception as e:
        logger.warning(f"{log_prefix}Could not delete old vectors: {e}")
        vectors_deleted = 0
    
    # Delete existing chunks from database
    old_chunks_result = await db.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    )
    old_chunks = old_chunks_result.scalars().all()
    old_chunk_count = len(old_chunks)
    
    for chunk in old_chunks:
        await db.delete(chunk)
    
    logger.debug(f"{log_prefix}Deleted {old_chunk_count} old chunks")
    
    # Extract text from file
    try:
        full_text, page_breaks = extract_pdf_text(file_path)
    except Exception as e:
        raise DocumentOperationError(f"PDF extraction failed: {e}")
    
    if not full_text.strip():
        raise DocumentOperationError("No text could be extracted from PDF")
    
    # Re-chunk
    chunks = chunk_text(full_text, chunk_size=600, chunk_overlap=100)
    if not chunks:
        raise DocumentOperationError("No chunks generated from document")
    
    # Get embeddings
    chunk_texts = [c[0] for c in chunks]
    embeddings = await get_embeddings(chunk_texts)
    
    # Create new chunk records
    source_ref = f"{document.source.value} - {document.name}"
    qdrant_chunks = []
    
    for idx, (chunk_text_content, char_start, char_end) in enumerate(chunks):
        page_num = determine_page(char_start, page_breaks)
        chunk_id = uuid.uuid4()
        
        chunk = DocumentChunk(
            id=chunk_id,
            document_id=document_id,
            chunk_index=idx,
            text=chunk_text_content,
            source=source_ref,
            page=page_num,
        )
        db.add(chunk)
        
        qdrant_chunks.append({
            "chunk_id": chunk_id,
            "document_id": document_id,
            "chunk_index": idx,
            "text": chunk_text_content,
            "source": source_ref,
            "page": page_num,
        })
    
    # Upsert to Qdrant
    await upsert_chunks(qdrant_chunks, embeddings)
    
    # Commit database changes
    await db.commit()
    
    logger.info(
        f"{log_prefix}✅ Reindexed document {document_id}: "
        f"{old_chunk_count} → {len(chunks)} chunks"
    )
    
    return {
        "document_id": str(document_id),
        "name": document.name,
        "old_chunks": old_chunk_count,
        "new_chunks": len(chunks),
        "vectors_deleted": vectors_deleted,
        "vectors_created": len(chunks),
    }
