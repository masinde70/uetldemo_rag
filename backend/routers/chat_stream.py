"""Streaming chat endpoint using Server-Sent Events (SSE).

This module provides a real-time streaming chat endpoint that sends
tokens as they are generated, enabling a ChatGPT-like experience.
"""

import json
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from backend.db import get_db
from backend.models import (
    AnalyticsSnapshot,
    ChatMessage,
    ChatMode,
    ChatSession,
    MessageRole,
    User,
    UserRole,
)
from backend.rag import hybrid_retrieve
from backend.services.auth import hash_password
from backend.services.llm_stream import stream_with_metadata

router = APIRouter(prefix="/api/chat", tags=["chat-stream"])

DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@uetcl.go.ug")


class StreamRequest(BaseModel):
    """Request model for streaming chat endpoint."""

    message: str
    mode: str = "strategy_qa"
    session_id: Optional[str] = None


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


def derive_session_title(message: str) -> str:
    """Derive session title from first message."""
    title = message[:50]
    if len(message) > 50:
        last_space = title.rfind(" ")
        if last_space > 20:
            title = title[:last_space]
        title += "..."
    return title


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
) -> list[dict]:
    """Get messages for a session."""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [{"role": msg.role.value, "content": msg.content} for msg in messages]


@router.post("/stream")
async def stream_chat(
    request: StreamRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Streaming chat endpoint using Server-Sent Events.

    Sends events:
    - start: {"sources": [...], "session_id": "..."}
    - token: {"content": "..."}
    - done: {"content": "full response", "sources": [...], "analytics": {...}}
    - error: {"message": "..."}

    The client should accumulate tokens to build the full response.
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
    await db.flush()

    # Get conversation history
    history = await get_session_messages(session.id, db)

    # Retrieve context
    chunks = await hybrid_retrieve(
        query=request.message,
        db=db,
        top_n=8,
        filters=None,
    )

    # Get analytics for analytics mode
    analytics_data = None
    if request.mode == "analytics":
        analytics_data = await get_latest_analytics(db)

    # Capture session_id for streaming
    session_id_str = str(session.id)

    async def event_generator():
        """Generate SSE events."""
        full_response = ""

        try:
            async for event in stream_with_metadata(
                messages=history,
                mode=request.mode,
                context_chunks=chunks,
                analytics_data=analytics_data,
            ):
                if event["type"] == "start":
                    # Add session_id to start event
                    event["data"]["session_id"] = session_id_str
                    yield {
                        "event": "start",
                        "data": json.dumps(event["data"]),
                    }

                elif event["type"] == "token":
                    full_response += event["data"]["content"]
                    yield {
                        "event": "token",
                        "data": json.dumps(event["data"]),
                    }

                elif event["type"] == "done":
                    # Store assistant message
                    assistant_message = ChatMessage(
                        session_id=session.id,
                        role=MessageRole.ASSISTANT,
                        content=full_response,
                    )
                    db.add(assistant_message)
                    await db.commit()

                    yield {
                        "event": "done",
                        "data": json.dumps(event["data"]),
                    }

        except Exception as e:
            await db.rollback()
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }

    return EventSourceResponse(event_generator())
