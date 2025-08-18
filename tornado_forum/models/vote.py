from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum
import enum

from models.base import Base
from .post import Topic, Comment
from .user import User 

class VoteType(enum.Enum):
    UPVOTE = 1
    NOVOTE = 0
    DOWNVOTE = -1

class VoteTopic(Base):
    __tablename__ = 'topic_votes'

    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    vote_type: Mapped[VoteType] = mapped_column(Enum(VoteType), default=VoteType.NOVOTE)

    topic: Mapped['Topic'] = relationship(back_populates='votes')
    user: Mapped['User'] = relationship(back_populates='topic_votes')


class VoteComment(Base):
    __tablename__ = 'comment_votes'

    comment_id: Mapped[int] = mapped_column(ForeignKey('comments.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    vote_type: Mapped[VoteType] = mapped_column(Enum(VoteType), default=VoteType.NOVOTE)

    comment: Mapped['Comment'] = relationship(back_populates='votes')
    user: Mapped['User'] = relationship(back_populates='comment_votes')