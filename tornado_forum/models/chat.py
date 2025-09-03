from sqlalchemy import String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .user import User

from .base import Base

class Room(Base):
    __tablename__ = 'chat_rooms'

    id:Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Text] = mapped_column(unique=True)
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'Room(id = {self.id},name = {self.name})'

class Message(Base):
    __tablename__ = 'messages'

    id:Mapped[int] = mapped_column(primary_key=True)
    data:Mapped[String] = mapped_column()
    room_id:Mapped[int] = mapped_column(ForeignKey('chat_rooms.id'))
    sender_id:Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())

    sender:Mapped['User'] = relationship('User', back_populates='sent_messages')

    def __repr__(self):
        return f'Message(id={self.id}, data={self.data})'
