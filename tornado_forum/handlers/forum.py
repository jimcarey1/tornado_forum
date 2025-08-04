import tornado
from sqlalchemy import insert, select

from .base import BaseHandler
from utils.permissions import is_admin

from models.forum import Forum
from models.post import Topic

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
        async with self.application.asession() as sess:
            query = insert(Forum).values(name=name, description=description)
            print(query.compile(compile_kwargs={'literal_binds':True}))
            forum = await sess.execute(query)
            await sess.commit()
            forum_id = forum.inserted_primary_key[0]
        self.redirect(f'/forum/{forum_id}')


class ViewForumHandler(BaseHandler):
    async def get(self, forum_id):
        print(f'The forum id {forum_id}')
        stmt = select(Forum).where(Forum.id == forum_id)
        print(stmt.compile(compile_kwargs={'literal_binds':True}))
        async with self.application.asession() as sess:
            forum = (await sess.execute(stmt)).one_or_none()
        self.render('forum/view_forum.html', forum=forum[0])