import tornado

from .base import BaseHandler
from utils.permissions import is_admin


class CreateForumHandler(BaseHandler):
    @tornado.web.authenticated
    @is_admin
    async def get(self):
        self.render('forum/create_forum.html')

    @tornado.web.authenticated
    @is_admin
    async def post(self):
        name = self.get_argument('name')
        description = self.get_argument('description')
        print(name, '\n', description)
        self.redirect('/forum/create')


class ViewForumHandler(BaseHandler):
    def get(self):
        pass