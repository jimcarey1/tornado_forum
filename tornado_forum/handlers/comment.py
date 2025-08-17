import tornado
from sqlalchemy import insert
import json

from .base import BaseHandler
from models.post import Comment

class CreateCommentHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, topic_id):
        data = json.loads(self.request.body)
        content = data.get('content', '')
        user_id = self.current_user.id
        async with self.application.asession() as sess:
            stmt = insert(Comment).values(content=content, topic_id=topic_id, user_id=user_id)
            # print(stmt.compile(compile_kwargs={'literal_binds':True}))
            comment_primary_key = await sess.execute(stmt)
            await sess.commit()
        print(comment_primary_key)
        self.set_header('Content-Type', 'application/json')
        self.write({'status': 'ok'})

class DeleteCommentHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, comment_id):
        pass

class CommentVoteHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, comment_id):
        pass
