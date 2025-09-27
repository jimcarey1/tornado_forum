from tornado.web import RequestHandler
from sqlalchemy import select
import tornado

from models.user import User

class BaseHandler(RequestHandler):
    async def prepare(self):
        user_id = self.get_signed_cookie("app_cookie")       
        if user_id and (not self.current_user):
            user_id = tornado.escape.to_unicode(user_id)
            async with self.application.asession() as sess:
                query = select(User.id, User.email, User.is_staff, User.is_admin, User.username).where(User.id==int(user_id))
                # print(query.compile(compile_kwargs={'literal_binds':True}))
                results = await sess.execute(query)
                user = results.one_or_none()
                self.current_user = user