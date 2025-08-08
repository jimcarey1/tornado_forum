import tornado
from sqlalchemy import insert, select

from .base import BaseHandler
from models.post import Topic


class CreateTopicHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, forum_id):
        self.render('post/create_post.html', forum_id=forum_id)

    @tornado.web.authenticated
    async def post(self, forum_id):
        title = self.get_argument('title')
        content = self.get_argument('content')
        forum_id = self.get_argument('forum_id')
        user_id = self.current_user.id
        async with self.application.asession() as sess:
            stmt = insert(Topic).values(title=title, content=content, forum_id=forum_id, user_id=user_id)
            post = await sess.execute(stmt)
            await sess.commit()
            print(post.inserted_primary_key)
        self.redirect(f'/topic/{post.inserted_primary_key[0]}')

class ViewTopicHanlder(BaseHandler):
    async def get(self, topic_id):
        async with self.application.asession() as sess:
            stmt = select(Topic).where(Topic.id == topic_id)
            topic = sess.scalar(stmt)
        self.render('post/view_post.html', topic=topic)