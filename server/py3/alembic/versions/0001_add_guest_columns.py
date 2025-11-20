"""add guest columns to sessions table

Revision ID: 0001_add_guest_columns
Revises: None
Create Date: 2025-11-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_guest_columns'
down_revision = None
branch_labels = None
depend_on = None


def upgrade() -> None:
    op.add_column('sessions', sa.Column('guest_id', sa.String(), nullable=True))
    op.add_column('sessions', sa.Column('guest_name', sa.String(), nullable=True))
    op.add_column('sessions', sa.Column('guest_icon', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_sessions_guest_id_users', 'sessions', 'users', ['guest_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_sessions_guest_id_users', 'sessions', type_='foreignkey')
    op.drop_column('sessions', 'guest_icon')
    op.drop_column('sessions', 'guest_name')
    op.drop_column('sessions', 'guest_id')
"""add guest columns to sessions table

Revision ID: 0001_add_guest_columns
Revises: None
Create Date: 2025-11-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_guest_columns'
down_revision = None
branch_labels = None
depend_on = None


def upgrade() -> None:
    op.add_column('sessions', sa.Column('guest_id', sa.String(), nullable=True))
    op.add_column('sessions', sa.Column('guest_name', sa.String(), nullable=True))
    op.add_column('sessions', sa.Column('guest_icon', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_sessions_guest_id_users', 'sessions', 'users', ['guest_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_sessions_guest_id_users', 'sessions', type_='foreignkey')
    op.drop_column('sessions', 'guest_icon')
    op.drop_column('sessions', 'guest_name')
    op.drop_column('sessions', 'guest_id')
