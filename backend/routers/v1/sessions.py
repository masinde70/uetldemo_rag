"""API v1 - Session management endpoints.

Provides endpoints for managing chat sessions and history.
"""

import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.models import ChatMessage, ChatSession, User, UserRole
from backend.services.auth import hash_password

router = APIRouter()

DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@uetcl.go.ug")


# --- Response Models ---


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


class SessionListResponse(BaseModel):
    """List of sessions response."""

    sessions: list[SessionInfo]
    total: int


class SessionHistoryResponse(BaseModel):
    """Session history response."""

    session_id: str
    title: Optional[str]
    mode: str
    messages: list[MessageInfo]


# --- Helper Functions ---


async def get_or_create_user(email: str, db: AsyncSession) -> User:
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


# --- Endpoints ---


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's chat sessions.

    Args:
        limit: Maximum sessions to return (default 50)
        offset: Offset for pagination

    Returns:
        SessionListResponse with sessions and total count
    """
    # Subquery for message count
    message_count = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.session_id == ChatSession.id)
        .correlate(ChatSession)
        .scalar_subquery()
    )

    # Get sessions
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
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Get total count
    count_stmt = (
        select(func.count(ChatSession.id))
        .where(ChatSession.user_id == user.id)
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    return SessionListResponse(
        sessions=[
            SessionInfo(
                id=str(row.id),
                title=row.title,
                mode=row.mode.value,
                created_at=row.created_at.isoformat(),
                message_count=row.message_count or 0,
            )
            for row in rows
        ],
        total=total,
    )


@router.get("/sessions/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get message history for a session.

    Args:
        session_id: The session UUID

    Returns:
        SessionHistoryResponse with session info and messages
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    # Get session
    stmt = select(ChatSession).where(
        ChatSession.id == session_uuid,
        ChatSession.user_id == user.id,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get messages
    msg_stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_uuid)
        .order_by(ChatMessage.created_at)
    )
    msg_result = await db.execute(msg_stmt)
    messages = msg_result.scalars().all()

    return SessionHistoryResponse(
        session_id=str(session.id),
        title=session.title,
        mode=session.mode.value,
        messages=[
            MessageInfo(
                id=str(msg.id),
                role=msg.role.value,
                content=msg.content,
                created_at=msg.created_at.isoformat(),
            )
            for msg in messages
        ],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session and its messages.

    Args:
        session_id: The session UUID

    Returns:
        Success message
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    # Get session
    stmt = select(ChatSession).where(
        ChatSession.id == session_uuid,
        ChatSession.user_id == user.id,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete messages first (foreign key)
    from sqlalchemy import delete

    await db.execute(
        delete(ChatMessage).where(ChatMessage.session_id == session_uuid)
    )

    # Delete session
    await db.delete(session)
    await db.commit()

    return {"message": "Session deleted successfully"}
