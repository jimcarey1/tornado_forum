from models.forum import Forum
from models.post import Topic

from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def is_root_forum(sess, forum_id:int)-> bool:
    stmt = select(Forum).where(Forum.id == forum_id)
    result = await sess.execute(stmt)
    forum = result.scalar_one_or_none()
    if forum and forum.parent_id is None:
        return True
    return False
    
async def get_forum_topics(sess, forum_id:int):
    parent_forum = await is_root_forum(sess, forum_id)
    if parent_forum:
        child_ids_subq = select(Forum.id).where(Forum.parent_id == forum_id).subquery()
        stmt = select(Topic).options(selectinload(Topic.forum), selectinload(Topic.user)).where(Topic.forum_id.in_(select(child_ids_subq.c.id))) \
                                                                .order_by(Topic.created_on.desc()).limit(5)
        # print(stmt.compile(compile_kwargs={'literal_binds':True}))
    else:
        stmt = select(Topic).options(selectinload(Topic.user)).where(Topic.forum_id == forum_id)
    topics = await sess.scalars(stmt)
    topics = topics.all()
    return topics