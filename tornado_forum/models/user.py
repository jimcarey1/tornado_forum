from sqlalchemy import String, Boolean, DateTime, Text
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

    google_oauth: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    access_token = mapped_column(Text, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=True)


    topics = relationship('Topic', back_populates='user')
    comments = relationship('Comment', back_populates='user')
    topic_votes = relationship('VoteTopic', back_populates='user')
    comment_votes = relationship('VoteComment', back_populates='user')

    sent_messages = relationship('Message', back_populates='sender')
    joined_rooms = relationship('RoomMember', back_populates='user')

    def __repr__(self):
        return f'User(id: {self.id}, username: {self.username})'