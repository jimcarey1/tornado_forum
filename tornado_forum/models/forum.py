from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func

from .base import Base
from .user import User

class Forum(Base):
    __tablename__ = 'forums'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description = mapped_column(Text)
    parent_id: Mapped[int] = mapped_column(ForeignKey('forums.id'), nullable=True)
    children = relationship('Forum', back_populates='parent')
    parent = relationship('Forum', back_populates='children', remote_side=[id])
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_on = mapped_column(DateTime(timezone=True), onupdate=func.now())

    topics = relationship('Topic', back_populates='forum')
    
    def __repr__(self):
        return f'Category(id: {self.id}, name: {self.name})'