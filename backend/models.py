"""SQLAlchemy 2.0 async models for SISUiQ."""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Computed,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# --- Enums ---

class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"


class ChatMode(str, enum.Enum):
    """Chat mode enumeration."""
    STRATEGY_QA = "strategy_qa"
    ACTIONS = "actions"
    ANALYTICS = "analytics"
    REGULATORY = "regulatory"


class MessageRole(str, enum.Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"


class DocumentType(str, enum.Enum):
    """Document type enumeration."""
    STRATEGY = "strategy"
    REGULATORY = "regulatory"
    TECHNICAL = "technical"
    REPORT = "report"
    POLICY = "policy"
    OTHER = "other"


class DocumentSource(str, enum.Enum):
    """Document source enumeration."""
    UETCL = "uetcl"
    ERA = "era"
    MEMD = "memd"
    WORLD_BANK = "world_bank"
    OTHER = "other"


# --- Utility functions ---

def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


# --- Models ---

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.USER,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    # Relationships
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class ChatSession(Base):
    """Chat session model grouping messages by conversation."""
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mode: Mapped[ChatMode] = mapped_column(
        Enum(ChatMode, name="chat_mode", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ChatMode.STRATEGY_QA,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    __table_args__ = (
        Index("ix_chat_sessions_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ChatSession {self.id} mode={self.mode.value}>"


class ChatMessage(Base):
    """Chat message model storing conversation history."""
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="message_role", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    # Relationships
    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages",
    )

    __table_args__ = (
        Index("ix_chat_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ChatMessage {self.id} role={self.role.value}>"


class Document(Base):
    """Document model for uploaded files metadata."""
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DocumentType.OTHER,
    )
    source: Mapped[DocumentSource] = mapped_column(
        Enum(DocumentSource, name="document_source", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DocumentSource.OTHER,
    )
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )

    # Relationships
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentChunk.chunk_index",
    )

    __table_args__ = (
        Index("ix_documents_type", "type"),
        Index("ix_documents_source", "source"),
    )

    def __repr__(self) -> str:
        return f"<Document {self.name}>"


class DocumentChunk(Base):
    """Document chunk model for RAG retrieval with FTS support."""
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Short source reference, e.g. 'UETCL Strategic Plan 2024-2029'",
    )
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # FTS vector - generated column for automatic updates
    # Note: This is defined as a regular column; the actual GENERATED ALWAYS AS
    # expression will be created in the migration for PostgreSQL-specific syntax
    fts_vector = mapped_column(
        TSVECTOR,
        nullable=True,
        comment="Full-text search vector, auto-generated from text",
    )

    # Relationships
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks",
    )

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
        Index("ix_document_chunks_document_id", "document_id"),
        Index("ix_document_chunks_page", "page"),
        # GIN index for FTS will be created in migration
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk doc={self.document_id} idx={self.chunk_index}>"


class AnalyticsSnapshot(Base):
    """Analytics snapshot model for processed data summaries."""
    __tablename__ = "analytics_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    dataset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Flexible JSON payload with summary statistics",
    )
    file_path: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        comment="Path to raw data file",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )

    __table_args__ = (
        Index("ix_analytics_snapshots_payload", "payload", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<AnalyticsSnapshot {self.dataset_name}>"
