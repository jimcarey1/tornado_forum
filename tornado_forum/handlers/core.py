from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base import BaseHandler
from models.forum import Forum

from handlers.services import is_root_forum, get_forum_topics

class HomeHandler(BaseHandler):
    async def get(self):
        query = select(Forum).where(Forum.parent == None).options(selectinload(Forum.children))
        async with self.application.asession() as sess:
            forums = await sess.scalars(query)
        self.render('core/home.html', forums=forums)