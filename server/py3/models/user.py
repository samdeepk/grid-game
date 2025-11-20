"""User model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """User model for storing user information."""

    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    icon = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    games = relationship('Game', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<User(id={self.id}, name={self.name})>'

