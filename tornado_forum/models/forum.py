from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func

from typing import Optional, List

from .base import Base
from .user import User
from .post import Topic

class Forum(Base):
    __tablename__ = 'forums'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(Text)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('forums.id'), nullable=True)
    children: Mapped[Optional[List['Forum']]] = relationship('Forum', back_populates='parent', lazy='selectin')
    parent: Mapped[Optional['Forum']] = relationship('Forum', back_populates='children', remote_side=[id])
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_on = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topics = relationship('Topic', back_populates='forum')
    
    def __repr__(self):
        return f'Forum(id: {self.id}, name: {self.name})'