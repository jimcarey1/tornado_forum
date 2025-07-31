from .base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        self.render('core/home.html')