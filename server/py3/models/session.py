"""Session model."""
from sqlalchemy import Column, DateTime, ForeignKey, String, func
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
    status = Column(String, nullable=False, default='WAITING')
    current_turn = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    host = relationship('User')

    def __repr__(self) -> str:
        return f'<Session(id={self.id}, status={self.status}, host_id={self.host_id})>'

