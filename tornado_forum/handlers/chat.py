import tornado
import json
import os
from typing import Dict
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from .base import BaseHandler
from models.chat import Message, Room, RoomMember
from models.user import User
from utils.rabbitmq import amqp_bind_room, send_to_client, list_all_server_ws, amqp_unbind_room, publish_message
from settings import room_subscribers

class ChatHandler(BaseHandler):
    def get(self):
        return self.render('chat/chat.html')

class UserListHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        async with self.application.asession() as session:
            stmt = select(User).order_by(User.username)
            result = await session.execute(stmt)
            users = result.scalars().all()
            user_list = [{"id": user.id, "username": user.username} for user in users if user.id != self.current_user.id]
            self.write({"users": user_list})

class DirectMessageHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        """
        Initiates a direct message room with another user.
        Expects a JSON body with {'user_id': <other_user_id>}.
        Returns {'room_id': <room_id>}.
        """
        try:
            data = json.loads(self.request.body)
            other_user_id = int(data['user_id'])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.send_error(400, reason="Invalid request body. Expected {'user_id': <int>}")
            return

        current_user_id = self.current_user.id
        if current_user_id == other_user_id:
            self.send_error(400, reason="Cannot start a chat with yourself.")
            return

        # Ensure the other user exists
        async with self.application.asession() as session:
            other_user = await session.get(User, other_user_id)
            if not other_user:
                self.send_error(404, reason="User not found.")
                return

        # Create a deterministic room name for the two users
        user_ids = sorted([current_user_id, other_user_id])
        room_name = f"dm_{user_ids[0]}_{user_ids[1]}"

        async with self.application.asession() as session:
            # Check if room already exists
            stmt = select(Room).where(Room.name == room_name)
            result = await session.execute(stmt)
            room = result.scalar_one_or_none()

            if room:
                self.write({'room_id': room.id})
                return

            # If not, create it
            try:
                new_room = Room(name=room_name)
                session.add(new_room)
                await session.flush() # To get the new_room.id

                # Add both users as members
                member1 = RoomMember(user_id=current_user_id, room_id=new_room.id)
                member2 = RoomMember(user_id=other_user_id, room_id=new_room.id)
                session.add_all([member1, member2])

                await session.commit()
                self.write({'room_id': new_room.id})
            except IntegrityError:
                await session.rollback()
                # This could happen in a race condition. Re-query for the room.
                stmt = select(Room).where(Room.name == room_name)
                result = await session.execute(stmt)
                room = result.scalar_one()
                self.write({'room_id': room.id})


class MessageHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        cookie = self.get_secure_cookie('app_cookie')
        if cookie:
            try:
                self.user_id = int(cookie.decode('utf-8'))
            except Exception as e:
                print(e)
                self.close(code=4002, reason='Invalid user cookie')
                return 
        self.subscribed_rooms = set()

    async def on_message(self, message):
        try:
            msg = json.loads(message) 
        except json.JSONDecodeError:
            return
        
        t = msg.get('type')
        if t == 'join':
            await self.handle_join(msg)
        if t == 'leave':
            await self.handle_leave(msg)
        if t == 'send':
            await self.handle_send(msg)

    
    async def on_close(self):
        for room_id in list(self.subscribed_rooms):
            await self._unsubscribe(room_id)

    async def handle_join(self, message:Dict):
        room_id = int(message.get('room_id'))
        room_subscribers.setdefault(room_id, set()).add(self)
        self.subscribed_rooms.add(room_id)

        await amqp_bind_room(room_id)
        await self.send_recent_history(room_id)
        await send_to_client(self, {'type':'joined', 'room_id':room_id})
    
    async def handle_leave(self, message:Dict):
        room_id = int(message.get('room_id'))
        await self._unsubscribe(room_id)
        await send_to_client(self, {'type':'left', 'room_id':room_id})
    
    async def _unsubscribe(self, room_id):
        if room_id in self.subscribed_rooms:
            room_subscribers.get(room_id, set()).discard(self)
            self.subscribed_rooms.discard(room_id)
            if not any(room_id in ws.subscribed_rooms for ws in list_all_server_ws()):
                await amqp_unbind_room(room_id)
    
    async def handle_send(self, message:Dict):
        room_id = int(message.get('room_id'))
        content = message.get('content', '')
        payload = {
            "room_id": room_id,
            "user_id": self.user_id,
            "data": content,
            "type": "chat"
        }
        await self.persist_message(payload)
        routing_key = f"room.{room_id}"
        await publish_message(payload, routing_key)
        await send_to_client(self, {"type": "sent_ack"})

    async def persist_message(self, payload):
        async with self.application.asession() as sess:
            msg = Message(
                room_id=payload['room_id'],
                sender_id=payload['user_id'],
                data=payload['data']
            )
            sess.add(msg)
            try:
                await sess.flush()
                pk = msg.id
                await sess.commit()
                return pk
            except IntegrityError:
                await sess.rollback()
                return None

    async def send_recent_history(self, room_id, limit=50):
        async with self.application.asession() as sess:
            stmt = (
                select(Message)
                .where(Message.room_id == room_id)
                .order_by(Message.created_on.desc())
                .limit(limit)
            )
            result = await sess.execute(stmt)
            rows = result.scalars().all()
        history = [
            {
                "message_id": str(r.id),
                "sender_id": r.sender_id,
                "data": r.data,
                "created_on": r.created_on.isoformat(),
            }
            for r in reversed(rows)
        ]
        await send_to_client(self, {"type": "history", "room_id": room_id, "messages": history})
