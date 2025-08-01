from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Text, DateTime
from sqlalchemy.sql import func

from models.base import Base
from models.user import User
from models.forum import Forum

class Topic(Base):
    __tablename__ = 'topics'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content = mapped_column(Text)
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_on = mapped_column(DateTime(timezone=True), onupdate=func.now())
    forum_id: Mapped[int] = mapped_column(ForeignKey('forums.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))

    forum: Mapped['Forum'] = relationship('Forum', back_populates='topics')
    user: Mapped['User'] = relationship('User', back_populates='topics')

    comments = relationship('Comment', back_populates='topic')


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content = mapped_column(Text)
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_on = mapped_column(DateTime(timezone=True), onupdate=func.now())
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))

    topic: Mapped['Topic'] = relationship('Topic', back_populates='comments')
    user: Mapped['User'] = relationship('User', back_populates='comments')