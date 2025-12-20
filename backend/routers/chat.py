"""Chat endpoints for the copilot."""
import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import (
    AnalyticsSnapshot,
    ChatMessage,
    ChatMode,
    ChatSession,
    DocumentSource,
    MessageRole,
    User,
    UserRole,
)
from backend.rag import hybrid_retrieve
from backend.services.auth import hash_password
from backend.services.llm import (
    build_context_prompt,
    build_system_prompt,
    chat_completion,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])

DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@uetcl.go.ug")


# --- Pydantic Models ---


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    mode: str = "strategy_qa"
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    """Source citation information."""

    citation: str
    page: Optional[int] = None
    source: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    answer: str
    session_id: str
    sources: List[str]
    analytics: Optional[dict] = None


class SessionInfo(BaseModel):
    """Session information."""

    id: str
    title: Optional[str]
    mode: str
    created_at: str
    message_count: int


class MessageInfo(BaseModel):
    """Message information."""

    id: str
    role: str
    content: str
    created_at: str


# --- Helper Functions ---


async def get_or_create_user(
    email: str,
    db: AsyncSession,
) -> User:
    """Get existing user or create demo user."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Create demo user with a random password (they won't login with it)
        user = User(
            email=email,
            name=email.split("@")[0].title(),
            role=UserRole.USER,
            password_hash=hash_password("demo-user-temp-password"),
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


def derive_session_title(message: str) -> str:
    """Derive session title from first message."""
    # Take first 50 chars, trim to word boundary
    title = message[:50]
    if len(message) > 50:
        # Find last space
        last_space = title.rfind(" ")
        if last_space > 20:
            title = title[:last_space]
        title += "..."
    return title


def get_source_filter(mode: str) -> Optional[dict]:
    """Get source filter based on chat mode.
    
    NOTE: Currently disabled because source field is stored as 
    "uetcl - docname" not just "uetcl", so exact match fails.
    TODO: Fix by either:
    1. Re-index docs with just source name in payload
    2. Use full-text index on source field in Qdrant
    """
    # Temporarily disabled - let RAG search all docs
    # if mode in ("strategy_qa", "actions", "analytics"):
    #     return {"source": DocumentSource.UETCL.value}
    # elif mode == "regulatory":
    #     return {"source": DocumentSource.ERA.value}
    return None


async def get_latest_analytics(
    db: AsyncSession,
    dataset_name: Optional[str] = None,
) -> Optional[dict]:
    """Get latest analytics snapshot."""
    stmt = select(AnalyticsSnapshot).order_by(AnalyticsSnapshot.created_at.desc())

    if dataset_name:
        stmt = stmt.where(AnalyticsSnapshot.dataset_name == dataset_name)

    stmt = stmt.limit(1)

    result = await db.execute(stmt)
    snapshot = result.scalar_one_or_none()

    if snapshot:
        return {
            "id": str(snapshot.id),
            "dataset_name": snapshot.dataset_name,
            "payload": snapshot.payload,
            "created_at": snapshot.created_at.isoformat(),
        }
    return None


async def get_session_messages(
    session_id: uuid.UUID,
    db: AsyncSession,
) -> List[dict]:
    """Get messages for a session."""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [
        {"role": msg.role.value, "content": msg.content}
        for msg in messages
    ]


# --- Endpoints ---


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Main chat endpoint.

    - Resolves user and session
    - Retrieves context via hybrid RAG
    - Generates response via LLM
    - Stores messages
    """
    # Validate mode
    try:
        mode_enum = ChatMode(request.mode)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Must be one of: {[m.value for m in ChatMode]}",
        )

    # Get or create session
    session: ChatSession
    if request.session_id:
        try:
            session_uuid = uuid.UUID(request.session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session_id format")

        stmt = select(ChatSession).where(
            ChatSession.id == session_uuid,
            ChatSession.user_id == user.id,
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

    else:
        # Create new session
        session = ChatSession(
            user_id=user.id,
            title=derive_session_title(request.message),
            mode=mode_enum,
        )
        db.add(session)
        await db.flush()

    # Store user message
    user_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_message)

    # Get conversation history
    history = await get_session_messages(session.id, db)
    # Add current message
    history.append({"role": "user", "content": request.message})

    # Retrieve context
    filters = get_source_filter(request.mode)
    chunks = await hybrid_retrieve(
        query=request.message,
        db=db,
        top_n=8,
        filters=filters,
    )

    # Get analytics for analytics mode
    analytics_data = None
    if request.mode == "analytics":
        analytics_data = await get_latest_analytics(db)

    # Build prompts
    system_prompt = build_system_prompt(
        mode=request.mode,
        has_analytics=analytics_data is not None,
    )
    context = build_context_prompt(
        chunks=chunks,
        analytics_summary=analytics_data,
    )

    # Generate response
    answer = await chat_completion(
        messages=history,
        system_prompt=system_prompt,
        context=context,
    )

    # Store assistant message
    assistant_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=answer,
    )
    db.add(assistant_message)

    # Extract unique sources
    sources = []
    seen_sources = set()
    for chunk in chunks:
        citation = chunk.get("citation", chunk.get("source", ""))
        if citation and citation not in seen_sources:
            sources.append(citation)
            seen_sources.add(citation)

    # Commit all changes
    await db.commit()

    return ChatResponse(
        answer=answer,
        session_id=str(session.id),
        sources=sources,
        analytics=analytics_data.get("payload") if analytics_data else None,
    )


@router.get("/sessions", response_model=List[SessionInfo])
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's chat sessions."""
    from sqlalchemy import func

    # Subquery for message count
    message_count = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.session_id == ChatSession.id)
        .correlate(ChatSession)
        .scalar_subquery()
    )

    stmt = (
        select(
            ChatSession.id,
            ChatSession.title,
            ChatSession.mode,
            ChatSession.created_at,
            message_count.label("message_count"),
        )
        .where(ChatSession.user_id == user.id)
        .order_by(ChatSession.created_at.desc())
        .limit(50)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        SessionInfo(
            id=str(row.id),
            title=row.title,
            mode=row.mode.value,
            created_at=row.created_at.isoformat(),
            message_count=row.message_count or 0,
        )
        for row in rows
    ]


@router.get("/history/{session_id}", response_model=List[MessageInfo])
async def get_history(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get message history for a session."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    # Verify session ownership
    stmt = select(ChatSession).where(
        ChatSession.id == session_uuid,
        ChatSession.user_id == user.id,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get messages
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_uuid)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [
        MessageInfo(
            id=str(msg.id),
            role=msg.role.value,
            content=msg.content,
            created_at=msg.created_at.isoformat(),
        )
        for msg in messages
    ]
