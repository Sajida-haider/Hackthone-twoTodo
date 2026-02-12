"""Create auth_events table

Revision ID: 004
Revises: 003
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create auth_events table."""
    op.create_table(
        'auth_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )

    # Create indexes
    op.create_index('idx_auth_events_user_id', 'auth_events', ['user_id'])
    op.create_index('idx_auth_events_event_type', 'auth_events', ['event_type'])
    op.create_index('idx_auth_events_created_at', 'auth_events', ['created_at'])
    op.create_index('idx_auth_events_user_created', 'auth_events', ['user_id', 'created_at'])


def downgrade() -> None:
    """Drop auth_events table."""
    op.drop_index('idx_auth_events_user_created', table_name='auth_events')
    op.drop_index('idx_auth_events_created_at', table_name='auth_events')
    op.drop_index('idx_auth_events_event_type', table_name='auth_events')
    op.drop_index('idx_auth_events_user_id', table_name='auth_events')
    op.drop_table('auth_events')
