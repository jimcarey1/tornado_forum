from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .user import User

from .base import Base

class Room(Base):
    __tablename__ = 'chat_rooms'

    id:Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())

    members = relationship('RoomMember', back_populates='room')

    def __repr__(self):
        return f'Room(id = {self.id}, name = {self.name})'

class RoomMember(Base):
    __tablename__ = 'room_members'

    user_id:Mapped[int] = mapped_column(ForeignKey('accounts.id', ondelete='CASCADE'), primary_key=True)
    room_id:Mapped[int] = mapped_column(ForeignKey('chat_rooms.id', ondelete='CASCADE'), primary_key=True)

    joined_on = mapped_column(DateTime(timezone=True), server_default=func.now())

    user:Mapped['User'] = relationship('User', back_populates='joined_rooms')
    room:Mapped['Room'] = relationship('Room', back_populates='members')



class Message(Base):
    __tablename__ = 'messages'

    id:Mapped[int] = mapped_column(primary_key=True)
    data:Mapped[str] = mapped_column()
    private:Mapped[bool] = mapped_column(default=True)
    room_id:Mapped[int] = mapped_column(ForeignKey('chat_rooms.id'))
    sender_id:Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())

    sender:Mapped['User'] = relationship('User', back_populates='sent_messages')

    def __repr__(self):
        return f'Message(id={self.id}, data={self.data})'
