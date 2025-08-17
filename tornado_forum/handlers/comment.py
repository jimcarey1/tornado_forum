import tornado
from sqlalchemy import insert

from .base import BaseHandler
from models.post import Comment

class CreateCommentHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, topic_id):
        content = self.get_argument('content')
        parent_id = self.get_argument('parent_id')
        user_id = self.current_user.id
        async with self.application.asession() as sess:
            stmt = insert(Comment).values(content=content, parent_id=parent_id, topic_id=topic_id, user_id=user_id)
            print(stmt.compile(compile_kwargs={'literal_binds':True}))
            comment_primary_key = await sess.execute(stmt)
            await sess.commit()
        self.redirect(f'/topic/{topic_id}')

class DeleteCommentHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, comment_id):
        pass

class CommentVoteHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, comment_id):
        pass
