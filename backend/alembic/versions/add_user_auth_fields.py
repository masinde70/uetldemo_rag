"""add password and auth fields to users

Revision ID: add_user_auth_fields
Revises: 
Create Date: 2024-12-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_user_auth_fields'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password_hash column with a default for existing rows
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))
    
    # Add is_active column
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    
    # Add last_login_at column
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add updated_at column
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Set default password hash for existing users (they'll need to reset)
    # Using bcrypt hash for "changeme"
    op.execute("""
        UPDATE users 
        SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4SFJbGvHHF4X.lLe',
            is_active = true,
            updated_at = NOW()
        WHERE password_hash IS NULL
    """)
    
    # Make password_hash non-nullable after setting defaults
    op.alter_column('users', 'password_hash', nullable=False)
    op.alter_column('users', 'is_active', nullable=False, server_default=None)


def downgrade() -> None:
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'password_hash')
