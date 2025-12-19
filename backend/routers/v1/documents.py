"""API v1 - Document management endpoints.

Provides endpoints for managing documents in the RAG system.
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import Document, DocumentSource, User, UserRole

router = APIRouter()

DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@uetcl.go.ug")


# --- Response Models ---


class DocumentInfo(BaseModel):
    """Document information."""

    id: str
    filename: str
    source: str
    status: str
    chunk_count: int
    created_at: str
    updated_at: str


class DocumentListResponse(BaseModel):
    """List of documents response."""

    documents: list[DocumentInfo]
    total: int


class DocumentUploadResponse(BaseModel):
    """Document upload response."""

    id: str
    filename: str
    message: str


# --- Helper Functions ---


async def get_or_create_user(email: str, db: AsyncSession) -> User:
    """Get existing user or create demo user."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            name=email.split("@")[0].title(),
            role=UserRole.USER,
        )
        db.add(user)
        await db.flush()

    return user


async def get_current_user(
    x_user_email: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user from header or use demo user."""
    email = x_user_email or DEMO_USER_EMAIL
    return await get_or_create_user(email, db)


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role for the endpoint."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )
    return user


# --- Endpoints ---


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    source: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List indexed documents.

    Args:
        source: Filter by document source (uetcl, era)
        status: Filter by status (pending, indexed, failed)
        limit: Maximum documents to return
        offset: Offset for pagination

    Returns:
        DocumentListResponse with documents and total count
    """
    # Build query
    stmt = select(Document)

    if source:
        try:
            source_enum = DocumentSource(source)
            stmt = stmt.where(Document.source == source_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source. Must be one of: {[s.value for s in DocumentSource]}",
            )

    if status:
        stmt = stmt.where(Document.status == status)

    # Get total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get documents
    stmt = stmt.order_by(Document.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[
            DocumentInfo(
                id=str(doc.id),
                filename=doc.filename,
                source=doc.source.value,
                status=doc.status,
                chunk_count=doc.chunk_count or 0,
                created_at=doc.created_at.isoformat(),
                updated_at=doc.updated_at.isoformat(),
            )
            for doc in documents
        ],
        total=total,
    )


@router.get("/documents/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get document details.

    Args:
        document_id: The document UUID

    Returns:
        DocumentInfo with document details
    """
    import uuid

    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document_id format")

    stmt = select(Document).where(Document.id == doc_uuid)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentInfo(
        id=str(document.id),
        filename=document.filename,
        source=document.source.value,
        status=document.status,
        chunk_count=document.chunk_count or 0,
        created_at=document.created_at.isoformat(),
        updated_at=document.updated_at.isoformat(),
    )


@router.get("/documents/sources")
async def list_sources():
    """List available document sources.

    Returns:
        List of source options
    """
    return {
        "sources": [
            {"id": source.value, "name": source.name}
            for source in DocumentSource
        ]
    }
