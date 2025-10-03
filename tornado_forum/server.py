import tornado
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pathlib import Path
from tornado.web import url

from handlers.user import UserLoginHandler, UserRegisterHandler, UserLogoutHandler, UserProfileHandler\
, FetchUserPostsHandler, FetchUserCommentsHandler, FetchUserUpVotedPosts, FetchUserDownVotedPosts,\
EmailVerificationHandler, SendVerificationMail

from handlers.core import HomeHandler
from handlers.forum import CreateForumHandler, ViewForumHandler
from handlers.post import CreateTopicHandler, ViewTopicHanlder, TopicVoteHandler
from handlers.comment import CreateCommentHandler, CommentModule, CommentVoteHandler, CommentChildrenHandler, DeleteCommentHandler
from handlers.chat import MessageHandler, ChatHandler, DirectMessageHandler, UserListHandler
from handlers.oauth import GoogleOAuth2LoginHandler, ChangeUsernameHandler

from utils.rabbitmq import init_amqp
from settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

BASE_PATH = Path(__file__).parent

class MyApplication(tornado.web.Application):
    def __init__(self, asession):
        self.asession = asession
        handlers = [
            (r'/', HomeHandler),
            (r'/auth/login', UserLoginHandler),
            url(r'/accounts/google/login/callback', GoogleOAuth2LoginHandler, name='google_oauth'),
            (r'/auth/register', UserRegisterHandler),
            (r'/auth/logout', UserLogoutHandler),
            (r'/change/username/(\d+)', ChangeUsernameHandler),
            (r'/api/topics/(\d+)', FetchUserPostsHandler),
            (r'/api/comments/(\d+)', FetchUserCommentsHandler),
            (r'/api/comments/delete/(\d+)', DeleteCommentHandler),
            (r'/api/upvoted_topics/(\d+)', FetchUserUpVotedPosts),
            (r'/api/downvoted_topics/(\d+)', FetchUserDownVotedPosts),
            (r'/verify', EmailVerificationHandler),
            (r'/send-verification-email', SendVerificationMail),
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
            (r'/api/users/(\d+)', UserListHandler),
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
            redirect_base_uri = 'http://localhost:8888',
            google_oauth = dict(key=GOOGLE_CLIENT_ID, secret=GOOGLE_CLIENT_SECRET)
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
    asyncio.run(main())