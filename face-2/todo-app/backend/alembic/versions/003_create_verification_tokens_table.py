"""Create verification_tokens table

Revision ID: 003
Revises: 002
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create verification_tokens table."""
    op.create_table(
        'verification_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index('idx_verification_tokens_user_id', 'verification_tokens', ['user_id'])
    op.create_index('idx_verification_tokens_token', 'verification_tokens', ['token'])
    op.create_index('idx_verification_tokens_expires_at', 'verification_tokens', ['expires_at'])


def downgrade() -> None:
    """Drop verification_tokens table."""
    op.drop_index('idx_verification_tokens_expires_at', table_name='verification_tokens')
    op.drop_index('idx_verification_tokens_token', table_name='verification_tokens')
    op.drop_index('idx_verification_tokens_user_id', table_name='verification_tokens')
    op.drop_table('verification_tokens')
