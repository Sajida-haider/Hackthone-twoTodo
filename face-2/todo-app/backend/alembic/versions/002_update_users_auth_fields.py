"""Update users table with authentication fields

Revision ID: 002
Revises: 001
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update users table with authentication fields."""
    # Drop old columns if they exist
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS username CASCADE;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS hashed_password CASCADE;")

    # Add new authentication columns
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=False, server_default=''))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))

    # Create indexes
    op.create_index('idx_users_is_verified', 'users', ['is_verified'])
    op.create_index('idx_users_locked_until', 'users', ['locked_until'])

    # Create trigger for automatic updated_at on users table
    op.execute("""
        CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Revert users table changes."""
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users;")
    op.drop_index('idx_users_locked_until', table_name='users')
    op.drop_index('idx_users_is_verified', table_name='users')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'password_hash')
