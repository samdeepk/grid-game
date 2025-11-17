"""Game model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from database import Base


class Game(Base):
    """Game model for storing game information."""

    __tablename__ = 'games'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    status = Column(String, default='active', nullable=False)  # active, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship('User', back_populates='games')

    def __repr__(self) -> str:
        return f'<Game(id={self.id}, name={self.name}, status={self.status})>'

