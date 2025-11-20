"""Session model."""
import json
from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, Text, func
from sqlalchemy.orm import relationship

from database import Base


class Session(Base):
    """Game session created by a host user."""

    __tablename__ = 'sessions'

    id = Column(String, primary_key=True, index=True)
    host_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    host_name = Column(String, nullable=False)
    host_icon = Column(String, nullable=True)
    game_icon = Column(String, nullable=True)
    game_type = Column(String, nullable=False, default='tic_tac_toe')  # For extensibility
    status = Column(String, nullable=False, default='WAITING')
    current_turn = Column(String, nullable=True)
    
    # Guest player fields
    guest_id = Column(String, ForeignKey('users.id'), nullable=True, index=True)
    guest_name = Column(String, nullable=True)
    guest_icon = Column(String, nullable=True)
    
    # Game state
    board = Column(Text, nullable=True)  # JSON string of board state
    winner = Column(String, nullable=True)
    draw = Column(Boolean, nullable=False, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    host = relationship('User', foreign_keys=[host_id])
    guest = relationship('User', foreign_keys=[guest_id])
    moves = relationship('Move', back_populates='session', order_by='Move.move_no', cascade='all, delete-orphan')

    def get_board(self) -> list:
        """Deserialize board from JSON string."""
        if not self.board:
            return self._get_default_board()
        try:
            return json.loads(self.board)
        except (json.JSONDecodeError, TypeError):
            return self._get_default_board()
    
    def set_board(self, board: list) -> None:
        """Serialize board to JSON string."""
        self.board = json.dumps(board)
    
    def _get_default_board(self) -> list:
        """Get default board based on game type."""
        if self.game_type == 'tic_tac_toe':
            return [[None, None, None], [None, None, None], [None, None, None]]
        # Add other game types here
        return [[None, None, None], [None, None, None], [None, None, None]]

    def __repr__(self) -> str:
        return f'<Session(id={self.id}, status={self.status}, host_id={self.host_id}, game_type={self.game_type})>'

