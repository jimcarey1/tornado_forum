import tornado

from .base import BaseHandler

class ChatHandler(BaseHandler):
    def get(self):
        return self.render('chat/chat.html')

class MessageHandler(tornado.websocket.WebSocketHandler):
    def open(self, room):
        self.room = room
        self.write_message('Hello World')

    def on_message(self, message):
        print(f'message recieved: {message}')
    
    def on_close(self):
        print('connection closed')