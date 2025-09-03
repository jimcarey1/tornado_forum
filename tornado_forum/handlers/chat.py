import tornado
import json
import os
from typing import Dict
from sqlalchemy.exc import IntegrityError

from .base import BaseHandler
from models.chat import Message, Room, RoomMember
from utils.rabbitmq import amqp_bind_room, send_to_client, list_all_server_ws, amqp_unbind_room, publish_message
from settings import room_subscribers

class ChatHandler(BaseHandler):
    def get(self):
        return self.render('chat/chat.html')

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
        print('websocket opened')

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
        content = message.get('cotent', '')
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
        async with self.application.assesion() as sess:
            msg = Message(
                room_id=payload['room_id'],
                sender_id=payload['user_id'],
                data=payload['data']
            )
            result = sess.add(msg)
            try:
                await sess.flush()
                pk = msg.id
                await sess.commit()
                return pk
            except IntegrityError:
                await sess.rollback()
                return None

    async def send_recent_history(self, ws, room_id, limit=50):
        async with self.application.asession() as sess:
            q = await sess.execute(
                "SELECT id, sender_id, data, created_on FROM messages WHERE room_id = :r ORDER BY created_at DESC LIMIT :l",
                {"r": room_id, "l": limit}
            )
            rows = q.fetchall()
        history = [{"message_id": str(r[0]), "sender_id": r[1], "data": r[2], "created_on": r[3].isoformat()} for r in reversed(rows)]
        await send_to_client(ws, {"type": "history", "room_id": room_id, "messages": history})
