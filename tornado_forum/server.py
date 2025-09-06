import tornado
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pathlib import Path

from handlers.user import UserLoginHandler, UserRegisterHandler, UserLogoutHandler, UserProfileHandler
from handlers.core import HomeHandler
from handlers.forum import CreateForumHandler, ViewForumHandler
from handlers.post import CreateTopicHandler, ViewTopicHanlder, TopicVoteHandler
from handlers.comment import CreateCommentHandler, CommentModule, CommentVoteHandler, CommentChildrenHandler
from handlers.chat import MessageHandler, ChatHandler, DirectMessageHandler, UserListHandler

from utils.rabbitmq import init_amqp

BASE_PATH = Path(__file__).parent

class MyApplication(tornado.web.Application):
    def __init__(self, asession):
        self.asession = asession
        handlers = [
            (r'/', HomeHandler),
            (r'/auth/login', UserLoginHandler),
            (r'/auth/register', UserRegisterHandler),
            (r'/auth/logout', UserLogoutHandler),
            (r'/forum/create', CreateForumHandler),
            (r'/forum/(\d+)', ViewForumHandler),
            (r'/topic/create/(\d+)', CreateTopicHandler),
            (r'/topic/(\d+)', ViewTopicHanlder),
            (r'/topic/(\d+)/comment/create', CreateCommentHandler),
            (r'/topic/(\d+)/vote', TopicVoteHandler),
            (r'/comment/(\d+)/vote', CommentVoteHandler),
            (r'/comment/(\d+)/children', CommentChildrenHandler),
            (r'/(\d+)/(\w+)', UserProfileHandler),
            (r'/chat', ChatHandler),
            (r'/chat/([a-zA-Z0-9_]+)', ChatHandler),
            (r'/api/chat/dm', DirectMessageHandler),
            (r'/api/users', UserListHandler),
            (r'/ws', MessageHandler)
        ]
        settings = dict(
            title = 'tornado forum',
            xsrf_cookies = True,
            debug = True,
            ui_modules = {'Comment': CommentModule},
            cookie_secret = 'DANGER, YOU ARE BEING CONSTANTLY WATCHED.',
            template_path = f'{BASE_PATH}/templates',
            static_path = f'{BASE_PATH}/static',
            login_url = '/auth/login',
        )
        super().__init__(handlers, **settings)


async def main():
    
    await init_amqp()
    async_engine = create_async_engine('sqlite+aiosqlite:///forum.sqlite')

    #we are using alembic to create and manage db migrations.
    # async with async_engine.connect() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
        
    asession = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    
    app = MyApplication(asession)
    app.listen(8888)

    shutdown_event = tornado.locks.Event()
    await shutdown_event.wait()
    
if __name__ == '__main__':
    asyncio.run(main(), debug=True)