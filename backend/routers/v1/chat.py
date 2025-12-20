"""API v1 - Chat endpoints.

Provides chat completion endpoints with RAG.
"""

import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents import route_to_agent
from backend.db import get_db
from backend.models import (
    ChatMessage,
    ChatMode,
    ChatSession,
    MessageRole,
    User,
    UserRole,
)
from backend.services.auth import hash_password

router = APIRouter()

DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@uetcl.go.ug")


# --- Request/Response Models ---


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(..., description="The user's message", min_length=1)
    mode: str = Field(
        default="strategy_qa",
        description="Chat mode: strategy_qa, actions, analytics, regulatory",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for continuing a conversation",
    )


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    answer: str = Field(..., description="The assistant's response")
    session_id: str = Field(..., description="Session ID for this conversation")
    sources: list[str] = Field(default=[], description="Source citations")
    agent: str = Field(..., description="Which agent handled the request")


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


def derive_session_title(message: str) -> str:
    """Derive session title from first message."""
    title = message[:50]
    if len(message) > 50:
        last_space = title.rfind(" ")
        if last_space > 20:
            title = title[:last_space]
        title += "..."
    return title


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


# --- Endpoints ---


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get an AI response.

    Uses the multi-agent architecture to route the query to the
    appropriate specialized agent based on the mode.

    Args:
        request: Chat request with message, mode, and optional session_id

    Returns:
        ChatResponse with answer, session_id, sources, and agent name
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

    # Get conversation history
    history = await get_session_messages(session.id, db)
    history.append({"role": "user", "content": request.message})

    # Route to appropriate agent
    agent_response = await route_to_agent(
        query=request.message,
        mode=request.mode,
        db=db,
        history=history,
    )

    # Store assistant message
    assistant_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.ASSISTANT,
        content=agent_response.answer,
    )
    db.add(assistant_message)

    await db.commit()

    return ChatResponse(
        answer=agent_response.answer,
        session_id=str(session.id),
        sources=agent_response.sources,
        agent=agent_response.agent_name,
    )


@router.get("/chat/modes")
async def list_modes():
    """List available chat modes.

    Returns:
        Dict with available modes and their descriptions
    """
    from backend.agents.orchestrator import MODE_AGENT_MAP

    return {
        "modes": [
            {
                "id": mode,
                "name": mode.replace("_", " ").title(),
                "description": agent_class.description,
            }
            for mode, agent_class in MODE_AGENT_MAP.items()
        ]
    }
