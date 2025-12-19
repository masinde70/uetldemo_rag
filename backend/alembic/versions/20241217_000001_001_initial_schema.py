"""Initial schema with all tables and FTS support.

Revision ID: 001
Revises:
Create Date: 2024-12-17 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'user')")
    op.execute("CREATE TYPE chat_mode AS ENUM ('strategy_qa', 'actions', 'analytics', 'regulatory')")
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant')")
    op.execute("CREATE TYPE document_type AS ENUM ('strategy', 'regulation', 'other')")
    op.execute("CREATE TYPE document_source AS ENUM ('UETCL', 'ERA', 'other')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'user', name='user_role', create_type=False), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('mode', postgresql.ENUM('strategy_qa', 'actions', 'analytics', 'regulatory', name='chat_mode', create_type=False), nullable=False, server_default='strategy_qa'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_chat_sessions_user_created', 'chat_sessions', ['user_id', 'created_at'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', name='message_role', create_type=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_chat_messages_session_created', 'chat_messages', ['session_id', 'created_at'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('type', postgresql.ENUM('strategy', 'regulation', 'other', name='document_type', create_type=False), nullable=False, server_default='other'),
        sa.Column('source', postgresql.ENUM('UETCL', 'ERA', 'other', name='document_source', create_type=False), nullable=False, server_default='other'),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_documents_type', 'documents', ['type'])
    op.create_index('ix_documents_source', 'documents', ['source'])
    op.create_index('ix_documents_created_at', 'documents', ['created_at'])

    # Create document_chunks table with FTS support
    op.create_table(
        'document_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('source', sa.String(500), nullable=True, comment="Short source reference"),
        sa.Column('page', sa.Integer(), nullable=True),
        sa.Column('fts_vector', postgresql.TSVECTOR(), nullable=True, comment="Full-text search vector"),
    )
    op.create_index('ix_document_chunks_document_id', 'document_chunks', ['document_id'])
    op.create_index('ix_document_chunks_page', 'document_chunks', ['page'])
    op.create_unique_constraint('uq_document_chunk_index', 'document_chunks', ['document_id', 'chunk_index'])

    # Create GIN index for FTS
    op.create_index(
        'ix_document_chunks_fts_vector',
        'document_chunks',
        ['fts_vector'],
        postgresql_using='gin'
    )

    # Create trigger to auto-update fts_vector when text changes
    op.execute("""
        CREATE OR REPLACE FUNCTION document_chunks_fts_update()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.fts_vector := to_tsvector('english', COALESCE(NEW.text, ''));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER document_chunks_fts_trigger
        BEFORE INSERT OR UPDATE OF text ON document_chunks
        FOR EACH ROW EXECUTE FUNCTION document_chunks_fts_update();
    """)

    # Create analytics_snapshots table
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dataset_name', sa.String(255), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('file_path', sa.String(1000), nullable=True, comment="Path to raw data file"),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_analytics_snapshots_dataset_name', 'analytics_snapshots', ['dataset_name'])
    op.create_index('ix_analytics_snapshots_created_at', 'analytics_snapshots', ['created_at'])
    op.create_index('ix_analytics_snapshots_payload', 'analytics_snapshots', ['payload'], postgresql_using='gin')


def downgrade() -> None:
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS document_chunks_fts_trigger ON document_chunks")
    op.execute("DROP FUNCTION IF EXISTS document_chunks_fts_update()")

    # Drop tables in reverse order of creation
    op.drop_table('analytics_snapshots')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('users')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS document_source")
    op.execute("DROP TYPE IF EXISTS document_type")
    op.execute("DROP TYPE IF EXISTS message_role")
    op.execute("DROP TYPE IF EXISTS chat_mode")
    op.execute("DROP TYPE IF EXISTS user_role")
