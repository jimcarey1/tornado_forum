from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from typing import List, Optional
from .base import Base


class User(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)

    topics = relationship('Topic', back_populates='user')
    comments = relationship('Comment', back_populates='user')

    def __repr__(self):
        return f'User(id: {self.id}, username: {self.username})'