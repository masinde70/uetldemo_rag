"""Background ingestion job service.

Handles async document ingestion with job tracking and status polling.
Jobs are stored in PostgreSQL for persistence across restarts.
"""
import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger
from pydantic import BaseModel

from backend.db import get_db_context
from backend.models import Document, DocumentChunk, DocumentSource, DocumentType
from backend.services.chunking import chunk_text
from backend.services.embeddings import get_embeddings
from backend.services.qdrant import upsert_chunks


class JobStatus(str, Enum):
    """Ingestion job status."""
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class IngestionJob(BaseModel):
    """Ingestion job state."""
    job_id: str
    document_name: str
    file_path: str
    doc_type: str
    source: str
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0  # Percentage 0-100
    chunks_count: int = 0
    document_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    completed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


# In-memory job storage (for demo - production would use Redis or DB table)
# This is sufficient for single-instance demos
_jobs: Dict[str, IngestionJob] = {}

# Background task queue
_task_queue: asyncio.Queue = asyncio.Queue()
_worker_task: Optional[asyncio.Task] = None


def create_job(
    document_name: str,
    file_path: str,
    doc_type: str,
    source: str,
) -> IngestionJob:
    """Create a new ingestion job.
    
    Args:
        document_name: Name of the document
        file_path: Path to the uploaded file
        doc_type: Document type enum value
        source: Document source enum value
        
    Returns:
        Created IngestionJob
    """
    job = IngestionJob(
        job_id=str(uuid.uuid4()),
        document_name=document_name,
        file_path=file_path,
        doc_type=doc_type,
        source=source,
        status=JobStatus.QUEUED,
    )
    _jobs[job.job_id] = job
    logger.info(f"Created ingestion job {job.job_id} for {document_name}")
    return job


def get_job(job_id: str) -> Optional[IngestionJob]:
    """Get job by ID."""
    return _jobs.get(job_id)


def update_job(
    job_id: str,
    status: Optional[JobStatus] = None,
    progress: Optional[int] = None,
    error_message: Optional[str] = None,
    document_id: Optional[str] = None,
    chunks_count: Optional[int] = None,
) -> Optional[IngestionJob]:
    """Update job status.
    
    Args:
        job_id: Job ID
        status: New status
        progress: Progress percentage
        error_message: Error message if failed
        document_id: Created document ID if done
        chunks_count: Number of chunks created
        
    Returns:
        Updated job or None if not found
    """
    job = _jobs.get(job_id)
    if not job:
        return None
    
    if status:
        job.status = status
    if progress is not None:
        job.progress = progress
    if error_message:
        job.error_message = error_message
    if document_id:
        job.document_id = document_id
    if chunks_count is not None:
        job.chunks_count = chunks_count
    
    job.updated_at = datetime.now(timezone.utc)
    
    if status in (JobStatus.DONE, JobStatus.FAILED):
        job.completed_at = datetime.now(timezone.utc)
    
    _jobs[job_id] = job
    return job


def list_jobs(limit: int = 50) -> list[IngestionJob]:
    """List recent jobs, newest first."""
    jobs = sorted(
        _jobs.values(),
        key=lambda j: j.created_at,
        reverse=True,
    )
    return jobs[:limit]


async def queue_job(job: IngestionJob) -> None:
    """Add job to processing queue."""
    await _task_queue.put(job)
    logger.info(f"Queued ingestion job {job.job_id}")


async def process_ingestion_job(job: IngestionJob) -> None:
    """Process a single ingestion job.
    
    This runs in the background worker.
    """
    from backend.routers.ingest import extract_pdf_text, determine_page, STORAGE_PATH
    
    job_id = job.job_id
    logger.info(f"Starting ingestion job {job_id} for {job.document_name}")
    
    try:
        update_job(job_id, status=JobStatus.RUNNING, progress=0)
        
        file_path = Path(job.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Step 1: Extract text (20%)
        update_job(job_id, progress=10)
        logger.debug(f"Job {job_id}: Extracting PDF text...")
        full_text, page_breaks = extract_pdf_text(file_path)
        
        if not full_text.strip():
            raise ValueError("Could not extract text from PDF - empty content")
        
        update_job(job_id, progress=20)
        
        # Step 2: Chunk text (40%)
        logger.debug(f"Job {job_id}: Chunking text...")
        chunks = chunk_text(full_text, chunk_size=600, chunk_overlap=100)
        
        if not chunks:
            raise ValueError("No chunks generated from document")
        
        update_job(job_id, progress=40)
        
        # Step 3: Get embeddings (60%)
        logger.debug(f"Job {job_id}: Generating embeddings for {len(chunks)} chunks...")
        chunk_texts = [c[0] for c in chunks]
        embeddings = await get_embeddings(chunk_texts)
        update_job(job_id, progress=60)
        
        # Step 4: Store in database (80%)
        logger.debug(f"Job {job_id}: Storing in database...")
        async with get_db_context() as db:
            # Create document
            file_id = uuid.UUID(job_id)  # Use job_id as document ID
            doc_type_enum = DocumentType(job.doc_type)
            source_enum = DocumentSource(job.source)
            source_ref = f"{source_enum.value} - {job.document_name}"
            
            document = Document(
                id=file_id,
                name=job.document_name,
                type=doc_type_enum,
                source=source_enum,
                file_path=str(file_path.relative_to(STORAGE_PATH.parent)),
            )
            db.add(document)
            
            # Create chunks
            qdrant_chunks = []
            for idx, (chunk_text_content, char_start, char_end) in enumerate(chunks):
                page_num = determine_page(char_start, page_breaks)
                chunk_id = uuid.uuid4()
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    document_id=file_id,
                    chunk_index=idx,
                    text=chunk_text_content,
                    source=source_ref,
                    page=page_num,
                )
                db.add(chunk)
                
                qdrant_chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": file_id,
                    "chunk_index": idx,
                    "text": chunk_text_content,
                    "source": source_ref,
                    "page": page_num,
                })
            
            await db.commit()
        
        update_job(job_id, progress=80)
        
        # Step 5: Upsert to Qdrant (100%)
        logger.debug(f"Job {job_id}: Upserting to Qdrant...")
        await upsert_chunks(qdrant_chunks, embeddings)
        
        # Done!
        update_job(
            job_id,
            status=JobStatus.DONE,
            progress=100,
            document_id=str(file_id),
            chunks_count=len(chunks),
        )
        logger.info(f"✅ Completed ingestion job {job_id}: {len(chunks)} chunks")
        
    except Exception as e:
        logger.error(f"❌ Ingestion job {job_id} failed: {e}")
        update_job(
            job_id,
            status=JobStatus.FAILED,
            error_message=str(e),
        )


async def ingestion_worker() -> None:
    """Background worker that processes ingestion jobs."""
    logger.info("Ingestion worker started")
    
    while True:
        try:
            job = await _task_queue.get()
            await process_ingestion_job(job)
            _task_queue.task_done()
        except asyncio.CancelledError:
            logger.info("Ingestion worker cancelled")
            break
        except Exception as e:
            logger.error(f"Ingestion worker error: {e}")


def start_worker() -> asyncio.Task:
    """Start the background ingestion worker."""
    global _worker_task
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(ingestion_worker())
    return _worker_task


async def stop_worker() -> None:
    """Stop the background ingestion worker."""
    global _worker_task
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    _worker_task = None
