"""Admin endpoints for dashboard.

Provides admin-only API endpoints for:
- Users management
- Session review
- Documents management
- Analytics snapshots

SECURITY NOTE: This is DEMO-ONLY authentication.
In production, use proper JWT/OAuth authentication.
See SECURITY_NOTES.md for production requirements.
"""
import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db import get_db
from backend.models import (
    AnalyticsSnapshot,
    ChatMessage,
    ChatSession,
    Document,
    DocumentChunk,
    User,
)
from backend.services.qdrant import delete_by_document_id

router = APIRouter(prefix="/api/admin", tags=["admin"])

# DEMO-ONLY: Simple token-based auth
# In production, use proper JWT/OAuth
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "demo-admin-token-change-me")


# --- Auth Dependency ---


async def get_current_user(
    x_admin_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
) -> User:
    """
    DEMO-ONLY admin verification.
    
    Supports both X-Admin-Token header and Authorization: Bearer token.
    In production, replace with proper JWT/OAuth authentication
    and role-based access control.
    """
    token = None
    
    # Check X-Admin-Token header first
    if x_admin_token:
        token = x_admin_token
    # Check Authorization: Bearer header
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    
    if not token or token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real app, we'd look up the user from the token
    # For demo, return a mock admin user
    return User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        email="admin@sisuiq.com",
        name="System Admin",
        role="admin",
    )


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user has admin role."""
    if str(current_user.role) != "admin" and current_user.role.value != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )
    return current_user


# --- Response Models ---


class PaginatedResponse(BaseModel):
    """Standard paginated response envelope."""
    data: list
    count: int


class UserItem(BaseModel):
    """User item for admin view."""
    id: str
    email: str
    name: str
    role: str
    created_at: str
    session_count: int = 0


class SessionListItem(BaseModel):
    """Session list item for admin view."""
    id: str
    user_email: str
    user_name: str
    mode: str
    title: Optional[str]
    message_count: int
    created_at: str


class MessageItem(BaseModel):
    """Message item for admin view."""
    id: str
    role: str
    content: str
    created_at: str


class DocumentItem(BaseModel):
    """Document item for admin view."""
    id: str
    name: str
    type: str
    source: str
    file_path: str
    chunk_count: int
    created_at: str


class AnalyticsItem(BaseModel):
    """Analytics snapshot item for admin view."""
    id: str
    dataset_name: str
    row_count: Optional[int]
    file_path: Optional[str]
    created_at: str
    summary: dict


# --- Endpoints ---


@router.get("/users")
async def list_users(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users with session counts.
    
    Returns:
        { "data": [...], "count": <total> }
    """
    # Subquery for session count
    session_count = (
        select(func.count(ChatSession.id))
        .where(ChatSession.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )

    # Get total count
    total_count = await db.scalar(select(func.count(User.id)))

    # Get paginated users
    stmt = (
        select(
            User.id,
            User.email,
            User.name,
            User.role,
            User.created_at,
            session_count.label("session_count"),
        )
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data = [
        UserItem(
            id=str(row.id),
            email=row.email,
            name=row.name,
            role=row.role.value if hasattr(row.role, 'value') else str(row.role),
            created_at=row.created_at.isoformat(),
            session_count=row.session_count or 0,
        ).model_dump()
        for row in rows
    ]

    return {"data": data, "count": total_count or 0}


@router.get("/sessions")
async def list_sessions(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all chat sessions with user info and message counts.
    
    Returns:
        { "data": [...], "count": <total> }
    """
    # Subquery for message count
    message_count = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.session_id == ChatSession.id)
        .correlate(ChatSession)
        .scalar_subquery()
    )

    # Get total count
    total_count = await db.scalar(select(func.count(ChatSession.id)))

    stmt = (
        select(
            ChatSession.id,
            ChatSession.title,
            ChatSession.mode,
            ChatSession.created_at,
            User.email.label("user_email"),
            User.name.label("user_name"),
            message_count.label("message_count"),
        )
        .join(User, User.id == ChatSession.user_id)
        .order_by(ChatSession.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data = [
        SessionListItem(
            id=str(row.id),
            user_email=row.user_email,
            user_name=row.user_name,
            mode=row.mode.value if hasattr(row.mode, 'value') else str(row.mode),
            title=row.title,
            message_count=row.message_count or 0,
            created_at=row.created_at.isoformat(),
        ).model_dump()
        for row in rows
    ]

    return {"data": data, "count": total_count or 0}


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all messages for a session.
    
    Returns:
        { "data": [...], "count": <total> }
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Use selectinload to efficiently load session with messages
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_uuid)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Messages are already loaded via selectinload
    data = [
        MessageItem(
            id=str(msg.id),
            role=msg.role.value if hasattr(msg.role, 'value') else str(msg.role),
            content=msg.content,
            created_at=msg.created_at.isoformat(),
        ).model_dump()
        for msg in sorted(session.messages, key=lambda m: m.created_at)
    ]

    return {"data": data, "count": len(data)}


@router.get("/documents")
async def list_documents(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all ingested documents with chunk counts.
    
    Returns:
        { "data": [...], "count": <total> }
    """
    # Subquery for chunk count
    chunk_count = (
        select(func.count(DocumentChunk.id))
        .where(DocumentChunk.document_id == Document.id)
        .correlate(Document)
        .scalar_subquery()
    )

    # Get total count
    total_count = await db.scalar(select(func.count(Document.id)))

    stmt = (
        select(
            Document.id,
            Document.name,
            Document.type,
            Document.source,
            Document.file_path,
            Document.created_at,
            chunk_count.label("chunk_count"),
        )
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data = [
        DocumentItem(
            id=str(row.id),
            name=row.name,
            type=row.type.value if hasattr(row.type, 'value') else str(row.type),
            source=row.source.value if hasattr(row.source, 'value') else str(row.source),
            file_path=row.file_path,
            chunk_count=row.chunk_count or 0,
            created_at=row.created_at.isoformat(),
        ).model_dump()
        for row in rows
    ]

    return {"data": data, "count": total_count or 0}


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document, its chunks, vectors, and stored file.
    """
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    document = await db.get(Document, doc_uuid)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Attempt to delete vectors in Qdrant
    vectors_deleted = 0
    try:
        vectors_deleted = await delete_by_document_id(doc_uuid)
    except Exception:
        # Do not block deletion if vector cleanup fails
        vectors_deleted = 0

    # Delete database record (chunks cascade)
    await db.delete(document)
    await db.commit()

    # Remove stored file (best effort)
    file_removed = False
    try:
        file_path = Path(document.file_path)
        if not file_path.is_absolute():
            file_path = Path(".") / file_path
        if file_path.exists():
            file_path.unlink()
            file_removed = True
    except Exception:
        file_removed = False

    return {
        "message": "Document deleted",
        "vectors_deleted": vectors_deleted,
        "file_removed": file_removed,
    }

@router.get("/analytics")
async def list_analytics(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all analytics snapshots.
    
    Returns:
        { "data": [...], "count": <total> }
    """
    # Get total count
    total_count = await db.scalar(select(func.count(AnalyticsSnapshot.id)))

    stmt = (
        select(AnalyticsSnapshot)
        .order_by(AnalyticsSnapshot.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    snapshots = result.scalars().all()

    data = [
        AnalyticsItem(
            id=str(snap.id),
            dataset_name=snap.dataset_name,
            row_count=snap.payload.get("row_count") if snap.payload else None,
            file_path=snap.file_path,
            created_at=snap.created_at.isoformat(),
            summary=snap.payload or {},
        ).model_dump()
        for snap in snapshots
    ]

    return {"data": data, "count": total_count or 0}


@router.get("/stats")
async def get_stats(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get overall system statistics.
    
    Returns:
        { users, sessions, messages, documents, chunks, analytics_snapshots }
    """
    # Get counts
    user_count = await db.scalar(select(func.count(User.id)))
    session_count = await db.scalar(select(func.count(ChatSession.id)))
    message_count = await db.scalar(select(func.count(ChatMessage.id)))
    doc_count = await db.scalar(select(func.count(Document.id)))
    chunk_count = await db.scalar(select(func.count(DocumentChunk.id)))
    analytics_count = await db.scalar(select(func.count(AnalyticsSnapshot.id)))

    return {
        "users": user_count or 0,
        "sessions": session_count or 0,
        "messages": message_count or 0,
        "documents": doc_count or 0,
        "chunks": chunk_count or 0,
        "analytics_snapshots": analytics_count or 0,
    }


# --- Document Lifecycle Endpoints ---


class DocumentDeleteResponse(BaseModel):
    """Response for document deletion."""
    document_id: str
    name: str
    chunks_deleted: int
    vectors_deleted: int
    message: str


class DocumentReindexResponse(BaseModel):
    """Response for document reindexing."""
    document_id: str
    name: str
    old_chunks: int
    new_chunks: int
    message: str


@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document and all associated data.
    
    Removes:
    - Document record from database
    - All chunk records (via cascade)
    - All vectors from Qdrant
    
    This operation cannot be undone.
    """
    from backend.services.document_ops import (
        delete_document as do_delete,
        DocumentNotFoundError,
        DocumentOperationError,
    )
    
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    try:
        result = await do_delete(db, doc_uuid, trace_id=document_id[:8])
        
        return DocumentDeleteResponse(
            document_id=result["document_id"],
            name=result["name"],
            chunks_deleted=result["chunks_deleted"],
            vectors_deleted=result["vectors_deleted"],
            message=f"Successfully deleted document '{result['name']}' with {result['chunks_deleted']} chunks",
        )
        
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    except DocumentOperationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/{document_id}/reindex", response_model=DocumentReindexResponse)
async def reindex_document(
    document_id: str,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Reindex a document by re-chunking and re-embedding.
    
    This will:
    - Delete existing chunks and vectors
    - Re-extract text from the stored PDF
    - Re-chunk with current settings
    - Generate new embeddings
    - Store new vectors in Qdrant
    
    Use this when:
    - Chunking parameters have changed
    - Embedding model has been updated
    - Document appears corrupted in search
    """
    from backend.services.document_ops import (
        reindex_document as do_reindex,
        DocumentNotFoundError,
        DocumentOperationError,
    )
    
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    try:
        result = await do_reindex(db, doc_uuid, trace_id=document_id[:8])
        
        return DocumentReindexResponse(
            document_id=result["document_id"],
            name=result["name"],
            old_chunks=result["old_chunks"],
            new_chunks=result["new_chunks"],
            message=f"Successfully reindexed document '{result['name']}': {result['old_chunks']} → {result['new_chunks']} chunks",
        )
        
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    except DocumentOperationError as e:
        raise HTTPException(status_code=500, detail=str(e))
