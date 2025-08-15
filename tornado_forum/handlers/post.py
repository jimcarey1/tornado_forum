import tornado
from sqlalchemy import insert, select
import json

from .base import BaseHandler
from models.post import Topic


class CreateTopicHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, forum_id):
        self.render('post/create_post.html', forum_id=forum_id)

    @tornado.web.authenticated
    async def post(self, forum_id):
        data = json.loads(self.request.body)
        title = data.get('title')
        content = data.get('content')
        user_id = self.current_user.id
        async with self.application.asession() as sess:
            stmt = insert(Topic).values(title=title, content=content, forum_id=int(forum_id), user_id=user_id)
            print(stmt.compile(compile_kwargs={'literal_binds': True}))
            post = await sess.execute(stmt)
            await sess.commit()
        post_id = post.inserted_primary_key[0]
        data = {"postId": post_id, "status": "ok"}
        json_string = json.dumps(data)
        self.set_header('Content-Type', 'application/json')
        self.write(json_string)

class ViewTopicHanlder(BaseHandler):
    async def get(self, topic_id):
        async with self.application.asession() as sess:
            stmt = select(Topic).where(Topic.id == topic_id)
            topic = await sess.execute(stmt)
            topic = topic.scalar_one_or_none()
            print(topic)
        self.render('post/view_post.html', topic=topic)