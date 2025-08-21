import tornado
from sqlalchemy import insert, select, func
import json

from .base import BaseHandler
from models.post import Comment
from models.vote import VoteComment, VoteType


class CreateCommentHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, topic_id):
        data = json.loads(self.request.body)
        content = data.get('content', '')
        parent_id = data.get('parent_id')
        user_id = self.current_user.id
        
        async with self.application.asession() as sess:
            async with sess.begin():
                stmt = insert(Comment).values(
                    content=content, 
                    topic_id=topic_id, 
                    user_id=user_id,
                    parent_id=parent_id
                ).returning(Comment)
                result = await sess.execute(stmt)
                new_comment = result.scalar_one()
                
                await sess.refresh(new_comment, attribute_names=['user'])
                
                comment_data = {
                    "id": new_comment.id,
                    "content": new_comment.content,
                    "user": {
                        "username": new_comment.user.username
                    },
                    "score": new_comment.score,
                    "parent_id": new_comment.parent_id,
                    "children": []
                }

        self.set_header('Content-Type', 'application/json')
        self.write(comment_data)

class DeleteCommentHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, comment_id):
        pass

class CommentVoteHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, comment_id):
        data = json.loads(self.request.body)
        vote_type = data.get('vote_type')
        user_id = self.current_user.id
        async with self.application.asession() as sess:
            stmt = select(VoteComment).where(VoteComment.comment_id == comment_id, VoteComment.user_id == user_id)
            result = await sess.execute(stmt)
            vote = result.scalar_one_or_none()
            if vote:
                if vote.vote_type.value == vote_type:
                    await sess.delete(vote)
                else:
                    vote.vote_type = VoteType(vote_type)
            else:
                vote = VoteComment(comment_id=comment_id, user_id=user_id, vote_type=VoteType(vote_type))
                sess.add(vote)
                print('We are adding the comment vote')

            await sess.flush()

            upvotes = await sess.execute(select(func.count(VoteComment.comment_id)).where(VoteComment.comment_id == comment_id, VoteComment.vote_type == VoteType.UPVOTE))
            downvotes = await sess.execute(select(func.count(VoteComment.comment_id)).where(VoteComment.comment_id == comment_id, VoteComment.vote_type == VoteType.DOWNVOTE))

            upvotes, downvotes = upvotes.scalar_one(), downvotes.scalar_one()

            comment = await sess.get(Comment, comment_id)
            comment.score = upvotes - downvotes

            await sess.commit()

        self.write({
            'upvotes': upvotes,
            'downvotes': downvotes,
        })


class CommentModule(tornado.web.UIModule):
    def render(self, comment):
        return self.render_string('modules/comment.html', comment=comment)