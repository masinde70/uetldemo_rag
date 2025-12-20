"""Document and data ingestion endpoints."""
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from pypdf import PdfReader
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import (
    AnalyticsSnapshot,
    Document,
    DocumentChunk,
    DocumentSource,
    DocumentType,
)
from backend.services.chunking import chunk_text
from backend.services.embeddings import get_embeddings
from backend.services.qdrant import upsert_chunks
from backend.services.ingestion_jobs import (
    JobStatus,
    IngestionJob,
    create_job,
    get_job,
    list_jobs,
    queue_job,
)

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])

STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "storage"))
DOCS_PATH = STORAGE_PATH / "docs"
DATA_PATH = STORAGE_PATH / "data"

# Ensure directories exist
DOCS_PATH.mkdir(parents=True, exist_ok=True)
DATA_PATH.mkdir(parents=True, exist_ok=True)


class DocumentResponse(BaseModel):
    """Response model for document ingestion."""

    id: str
    name: str
    type: str
    source: str
    chunks_count: int
    message: str


class DataResponse(BaseModel):
    """Response model for data ingestion."""

    id: str
    dataset_name: str
    file_path: str
    summary: dict
    message: str


def extract_pdf_text(file_path: Path) -> tuple[str, list[int]]:
    """
    Extract text from PDF file using pypdf, pdfplumber, or OCR as fallback.

    Args:
        file_path: Path to PDF file

    Returns:
        Tuple of (full_text, page_breaks) where page_breaks is list of char positions
    """
    full_text = ""
    page_breaks = []
    
    # Try pypdf first (fastest for embedded text)
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_breaks.append(len(full_text))
            page_text = page.extract_text() or ""
            full_text += page_text + "\n\n"
    except Exception:
        pass  # Fall through to pdfplumber
    
    # If pypdf didn't extract much text, try pdfplumber
    if len(full_text.strip()) < 100:
        full_text = ""
        page_breaks = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_breaks.append(len(full_text))
                    page_text = page.extract_text() or ""
                    full_text += page_text + "\n\n"
        except Exception:
            pass  # Fall through to OCR
    
    # If still no text, try OCR (for scanned PDFs)
    if len(full_text.strip()) < 100:
        full_text = ""
        page_breaks = []
        try:
            # Process one page at a time to reduce memory usage
            # Use lower DPI (150 instead of 200) to save memory
            from pdf2image.pdf2image import pdfinfo_from_path
            import gc

            info = pdfinfo_from_path(file_path)
            num_pages = info.get("Pages", 1)

            for page_num in range(1, num_pages + 1):
                page_breaks.append(len(full_text))
                # Convert single page at a time
                images = convert_from_path(
                    file_path,
                    dpi=150,  # Lower DPI to reduce memory
                    first_page=page_num,
                    last_page=page_num
                )
                if images:
                    page_text = pytesseract.image_to_string(images[0]) or ""
                    full_text += page_text + "\n\n"
                    # Explicitly free memory
                    del images
                    gc.collect()
        except Exception as e:
            raise RuntimeError(f"OCR extraction failed: {e}")

    return full_text.strip(), page_breaks


def determine_page(char_start: int, page_breaks: list[int]) -> int | None:
    """Determine page number from character position."""
    if not page_breaks:
        return None
    for i, break_pos in enumerate(page_breaks):
        if char_start < break_pos:
            return i  # 0-indexed page before this break
    return len(page_breaks)  # Last page


@router.post("/docs", response_model=DocumentResponse)
async def ingest_document(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    doc_type: str = Form("other"),
    source: str = Form("other"),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a PDF document.

    - Stores the file
    - Extracts text
    - Chunks the text
    - Creates embeddings
    - Stores in Qdrant and Postgres
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Validate enums
    try:
        doc_type_enum = DocumentType(doc_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document type. Must be one of: {[t.value for t in DocumentType]}",
        )

    try:
        source_enum = DocumentSource(source)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source. Must be one of: {[s.value for s in DocumentSource]}",
        )

    # Generate file ID and path
    file_id = uuid.uuid4()
    file_path = DOCS_PATH / f"{file_id}.pdf"

    # Save file
    content = await file.read()
    file_path.write_bytes(content)

    try:
        # Extract text from PDF
        try:
            full_text, page_breaks = extract_pdf_text(file_path)
        except Exception as e:
            file_path.unlink()  # Clean up
            raise HTTPException(status_code=400, detail=f"PDF extraction error: {str(e)}")

        if not full_text.strip():
            file_path.unlink()  # Clean up
            raise HTTPException(status_code=400, detail="Could not extract text from PDF - empty content")

        # Chunk the text
        chunks = chunk_text(full_text, chunk_size=600, chunk_overlap=100)

        if not chunks:
            file_path.unlink()
            raise HTTPException(status_code=400, detail="No chunks generated from document")

        # Determine document name
        doc_name = name or file.filename or f"document_{file_id}"

        # Create source reference
        source_ref = f"{source_enum.value} - {doc_name}"

        # Create document record
        document = Document(
            id=file_id,
            name=doc_name,
            type=doc_type_enum,
            source=source_enum,
            file_path=str(file_path.relative_to(STORAGE_PATH.parent)),
        )
        db.add(document)

        # Prepare chunks for embedding and storage
        chunk_texts = [c[0] for c in chunks]

        # Get embeddings
        embeddings = await get_embeddings(chunk_texts)

        # Create chunk records and prepare for Qdrant
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

        # Upsert to Qdrant
        await upsert_chunks(qdrant_chunks, embeddings)

        # Commit database transaction
        await db.commit()

        return DocumentResponse(
            id=str(file_id),
            name=doc_name,
            type=doc_type_enum.value,
            source=source_enum.value,
            chunks_count=len(chunks),
            message=f"Successfully ingested document with {len(chunks)} chunks",
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/data", response_model=DataResponse)
async def ingest_data(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a tabular data file (CSV or XLSX).

    - Stores the raw file
    - Creates analytics_snapshot with summary stats
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    ext = Path(file.filename).suffix.lower()
    allowed_exts = {".csv", ".xlsx"}
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Only CSV or XLSX files are supported")

    # Generate file ID and path (preserve extension)
    file_id = uuid.uuid4()
    file_path = DATA_PATH / f"{file_id}{ext}"

    # Save file
    content = await file.read()
    file_path.write_bytes(content)

    try:
        # Read file for summary
        if ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, engine="openpyxl")

        # Clean columns: drop empty, replace "Unnamed" with generic
        df = df.dropna(axis=1, how="all")
        cleaned_cols = []
        for idx, col in enumerate(df.columns):
            name = str(col)
            if name.startswith("Unnamed") or name.strip() == "":
                name = f"column_{idx+1}"
            cleaned_cols.append(name)
        df.columns = cleaned_cols

        # Build summary payload
        payload: dict = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        }

        # Add date range if date columns exist
        date_columns = df.select_dtypes(include=["datetime64"]).columns.tolist()
        for col in df.columns:
            if "date" in col.lower() or "time" in col.lower():
                try:
                    dates = pd.to_datetime(df[col], errors="coerce")
                    valid_dates = dates.dropna()
                    if not valid_dates.empty:
                        payload["date_range"] = {
                            "column": col,
                            "min": str(valid_dates.min()),
                            "max": str(valid_dates.max()),
                        }
                        break
                except Exception:
                    pass

        # Add category counts for string columns (first few)
        for col in df.select_dtypes(include=["object"]).columns[:3]:
            value_counts = df[col].value_counts().head(5).to_dict()
            if value_counts:
                payload.setdefault("category_counts", {})[col] = {
                    str(k): int(v) for k, v in value_counts.items()
                }

        # Add numeric summaries
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            payload["numeric_summary"] = {}
            for col in numeric_cols[:5]:  # First 5 numeric columns
                payload["numeric_summary"][col] = {
                    "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                }
        
        # Add preview rows (first 5)
        preview_rows = df.head(5).fillna("").to_dict(orient="records")
        payload["preview_rows"] = preview_rows

        # Determine dataset name
        name = dataset_name or Path(file.filename).stem or f"dataset_{file_id}"

        # Create analytics snapshot
        snapshot = AnalyticsSnapshot(
            id=file_id,
            dataset_name=name,
            payload=payload,
            file_path=str(file_path.relative_to(STORAGE_PATH.parent)),
        )
        db.add(snapshot)
        await db.commit()

        return DataResponse(
            id=str(file_id),
            dataset_name=name,
            file_path=str(file_path),
            summary=payload,
            message=f"Successfully ingested data with {payload['row_count']} rows",
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")


# --- Background Job Endpoints ---


class JobQueueResponse(BaseModel):
    """Response when document is queued for background ingestion."""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Response for job status check."""
    job_id: str
    status: str
    progress: int
    document_name: str
    document_id: Optional[str] = None
    chunks_count: int = 0
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None


class JobListResponse(BaseModel):
    """Response for job list."""
    jobs: list[JobStatusResponse]
    count: int


@router.post("/docs/async", response_model=JobQueueResponse)
async def ingest_document_async(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    doc_type: str = Form("other"),
    source: str = Form("other"),
):
    """
    Queue a PDF document for background ingestion.
    
    Returns immediately with a job_id that can be polled for status.
    Use GET /api/ingest/jobs/{job_id} to check progress.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate enums
    try:
        DocumentType(doc_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document type. Must be one of: {[t.value for t in DocumentType]}",
        )
    
    try:
        DocumentSource(source)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source. Must be one of: {[s.value for s in DocumentSource]}",
        )
    
    # Generate file path and save
    file_id = uuid.uuid4()
    file_path = DOCS_PATH / f"{file_id}.pdf"
    
    content = await file.read()
    file_path.write_bytes(content)
    
    # Determine document name
    doc_name = name or file.filename or f"document_{file_id}"
    
    # Create and queue job
    job = create_job(
        document_name=doc_name,
        file_path=str(file_path),
        doc_type=doc_type,
        source=source,
    )
    
    await queue_job(job)
    
    return JobQueueResponse(
        job_id=job.job_id,
        status=job.status.value if hasattr(job.status, 'value') else str(job.status),
        message=f"Document '{doc_name}' queued for processing",
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of an ingestion job.
    
    Poll this endpoint to track background ingestion progress.
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value if hasattr(job.status, 'value') else str(job.status),
        progress=job.progress,
        document_name=job.document_name,
        document_id=job.document_id,
        chunks_count=job.chunks_count,
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )


@router.get("/jobs", response_model=JobListResponse)
async def list_ingestion_jobs(limit: int = 50):
    """
    List recent ingestion jobs.
    
    Returns jobs sorted by creation time (newest first).
    """
    jobs = list_jobs(limit=limit)
    
    return JobListResponse(
        jobs=[
            JobStatusResponse(
                job_id=j.job_id,
                status=j.status.value if hasattr(j.status, 'value') else str(j.status),
                progress=j.progress,
                document_name=j.document_name,
                document_id=j.document_id,
                chunks_count=j.chunks_count,
                error_message=j.error_message,
                created_at=j.created_at.isoformat(),
                updated_at=j.updated_at.isoformat(),
                completed_at=j.completed_at.isoformat() if j.completed_at else None,
            )
            for j in jobs
        ],
        count=len(jobs),
    )
