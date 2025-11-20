"""add game_type, board, winner, draw columns to sessions

Revision ID: 0002_add_session_fields
Revises: 0001_add_guest_columns
Create Date: 2025-11-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_session_fields'
down_revision = '0001_add_guest_columns'
branch_labels = None
depend_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column('sessions', sa.Column('game_type', sa.String(), nullable=False, server_default=sa.text("'tic_tac_toe'")))
    op.add_column('sessions', sa.Column('board', sa.Text(), nullable=True))
    op.add_column('sessions', sa.Column('winner', sa.String(), nullable=True))
    op.add_column('sessions', sa.Column('draw', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')))

    # Optionally, initialize board for existing sessions where needed
    # Note: update default board for all existing sessions to NULL or a default value.
    # We'll initialize empty boards for any waiting sessions.
    op.execute("UPDATE sessions SET game_type='tic_tac_toe' WHERE game_type IS NULL;")
    op.execute("UPDATE sessions SET draw=false WHERE draw IS NULL;")


def downgrade() -> None:
    op.drop_column('sessions', 'draw')
    op.drop_column('sessions', 'winner')
    op.drop_column('sessions', 'board')
    op.drop_column('sessions', 'game_type')
