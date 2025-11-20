"""Move model for tracking game moves."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from database import Base


class Move(Base):
    """Move model for tracking individual moves in a game session."""

    __tablename__ = 'moves'

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False, index=True)
    player_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    row = Column(Integer, nullable=False)
    col = Column(Integer, nullable=False)
    move_no = Column(Integer, nullable=False)  # Sequential move number (1, 2, 3, ...)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship('Session', back_populates='moves')
    player = relationship('User')

    def __repr__(self) -> str:
        return f'<Move(id={self.id}, session_id={self.session_id}, player_id={self.player_id}, move_no={self.move_no})>'

