import tornado

from .base import BaseHandler


class CreateTopicHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('post/create_post.html')

    @tornado.web.authenticated
    def post(self):
        pass

class ViewTopicHanlder(BaseHandler):
    def get(self):
        pass