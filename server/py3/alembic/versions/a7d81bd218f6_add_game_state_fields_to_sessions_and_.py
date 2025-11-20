"""Add game state fields to sessions and create moves table

Revision ID: a7d81bd218f6
Revises: 
Create Date: 2025-11-19 19:49:24.973017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a7d81bd218f6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()
    
    # Check if moves table exists
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    moves_exists = 'moves' in tables
    
    # Check which columns exist in sessions table
    if 'sessions' in tables:
        columns = [col['name'] for col in inspector.get_columns('sessions')]
    else:
        columns = []
    
    # Add new columns to sessions table (only if they don't exist)
    if 'game_type' not in columns:
        op.add_column('sessions', sa.Column('game_type', sa.String(), nullable=False, server_default='tic_tac_toe'))
    if 'guest_id' not in columns:
        op.add_column('sessions', sa.Column('guest_id', sa.String(), nullable=True))
    if 'guest_name' not in columns:
        op.add_column('sessions', sa.Column('guest_name', sa.String(), nullable=True))
    if 'guest_icon' not in columns:
        op.add_column('sessions', sa.Column('guest_icon', sa.String(), nullable=True))
    if 'board' not in columns:
        op.add_column('sessions', sa.Column('board', sa.Text(), nullable=True))
    if 'winner' not in columns:
        op.add_column('sessions', sa.Column('winner', sa.String(), nullable=True))
    if 'draw' not in columns:
        op.add_column('sessions', sa.Column('draw', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    
    # Create index and foreign key for guest_id (only if guest_id column was just added or index doesn't exist)
    if 'guest_id' in columns or 'guest_id' not in columns:
        # Check if index exists
        indexes = [idx['name'] for idx in inspector.get_indexes('sessions')] if 'sessions' in tables else []
        if 'ix_sessions_guest_id' not in indexes:
            op.create_index(op.f('ix_sessions_guest_id'), 'sessions', ['guest_id'], unique=False)
        
        # Check if foreign key exists
        foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('sessions')] if 'sessions' in tables else []
        if 'sessions_guest_id_fkey' not in foreign_keys:
            op.create_foreign_key('sessions_guest_id_fkey', 'sessions', 'users', ['guest_id'], ['id'])
    
    # Create moves table (only if it doesn't exist)
    if not moves_exists:
        op.create_table('moves',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('session_id', sa.String(), nullable=False),
            sa.Column('player_id', sa.String(), nullable=False),
            sa.Column('row', sa.Integer(), nullable=False),
            sa.Column('col', sa.Integer(), nullable=False),
            sa.Column('move_no', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['player_id'], ['users.id'], name='moves_player_id_fkey'),
            sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name='moves_session_id_fkey', ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id', name='moves_pkey')
        )
        op.create_index(op.f('ix_moves_session_id'), 'moves', ['session_id'], unique=False)
        op.create_index(op.f('ix_moves_player_id'), 'moves', ['player_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop moves table
    op.drop_index(op.f('ix_moves_player_id'), table_name='moves')
    op.drop_index(op.f('ix_moves_session_id'), table_name='moves')
    op.drop_table('moves')
    
    # Drop columns from sessions table
    op.drop_constraint('sessions_guest_id_fkey', 'sessions', type_='foreignkey')
    op.drop_index(op.f('ix_sessions_guest_id'), table_name='sessions')
    op.drop_column('sessions', 'draw')
    op.drop_column('sessions', 'winner')
    op.drop_column('sessions', 'board')
    op.drop_column('sessions', 'guest_icon')
    op.drop_column('sessions', 'guest_name')
    op.drop_column('sessions', 'guest_id')
    op.drop_column('sessions', 'game_type')
