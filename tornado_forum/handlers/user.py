from sqlalchemy import select, insert, or_
import tornado
import bcrypt


from .base import BaseHandler
from models.user import User


class UserRegisterHandler(BaseHandler):
    def get(self):
        '''
        If the user already logged in, redirect him to the homepage.
        '''
        self.render('user/register.html')

    async def post(self):
        username = self.get_argument('username')
        email = self.get_argument('email')
        password = self.get_argument('password')
        async with self.application.asession() as asess:
            query = select(User).where(or_(User.username == username, User.email == email))
            print(query.compile(compile_kwargs={'literal_binds':True}))
            result = (await asess.execute(query)).first()
        if result is not None:
            #A user with username or email already exist.
            self.render('user/register.html')
        else:
            #Create user and auto login.
            hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
                None,
                bcrypt.hashpw,
                tornado.escape.utf8(password),
                bcrypt.gensalt()
            )
            async with self.application.asession() as asess:
                query = insert(User).values(username=username, email=email, password=tornado.escape.to_unicode(hashed_password))
                print(query.compile(compile_kwargs={'literal_binds':True}))
                user = await asess.execute(query)
                await asess.commit()
            self.set_signed_cookie("app_cookie", str(user.inserted_primary_key[0]))
            self.redirect('/')

class UserLoginHandler(BaseHandler):
    def get(self):
        '''
        If the user already logged in, redirect him to the homepage.
        '''
        self.render('user/login.html')

    async def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        async with self.application.asession() as sess:
            query = select(User.id, User.password).where(User.username == username)
            # print(query.compile(compile_kwargs={'literal_binds':True}))
            try:
                result = (await sess.execute(query)).one_or_none()
                print(result)
            except Exception as e:
                print(f'got exception: {e}')
                pass
        password_check = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.checkpw,
            tornado.escape.utf8(password),
            tornado.escape.utf8(result.password)
        )
        if password_check:
            self.set_signed_cookie('app_cookie', str(result.id))
            self.redirect('/')
        self.redirect('/auth/login')

class UserLogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie('app_cookie')
        self.redirect('/auth/login')