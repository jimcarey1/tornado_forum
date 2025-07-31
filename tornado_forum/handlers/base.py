from tornado.web import RequestHandler
from sqlalchemy import select
import tornado

from models.user import User

class BaseHandler(RequestHandler):
    async def prepare(self):
        # get_current_user cannot be a coroutine, so set
        # self.current_user in prepare instead.
        user_id = self.get_signed_cookie("app_cookie")
        if user_id and (not self.current_user):
            user_id = tornado.escape.to_unicode(user_id)
            async with self.application.asession() as sess:
                query = select(User).where(User.id==int(user_id))
                print(query.compile(compile_kwargs={'literal_binds':True}))
                user = await sess.scalar(query)
                self.current_user = user