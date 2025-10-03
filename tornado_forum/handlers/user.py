from sqlalchemy import select, insert, or_
from sqlalchemy.orm import selectinload
import tornado
from tornado import ioloop
import bcrypt
import json


from .base import BaseHandler
from models.user import User
from models.post import Topic, Comment
from models.vote import VoteTopic, VoteType
from utils.email_verification import confirm_verification_token, generate_verification_token, send_verification_email


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
        async with self.application.asession() as sess:
            query = select(User).where(or_(User.username == username, User.email == email))
            result = await sess.execute(query)
            result = result.scalar_one_or_none()
        if result is not None:
            #A user with username or email already exist.
            self.render('user/register.html')
        else:
            #Create user and auto login.
            hashed_password = await ioloop.IOLoop.current().run_in_executor(
                None,
                bcrypt.hashpw,
                tornado.escape.utf8(password),
                bcrypt.gensalt()
            )
            async with self.application.asession() as asess:
                user = User(
                    username=username, 
                    email=email, 
                    password=tornado.escape.to_unicode(hashed_password),
                    can_change_username = False,
                    email_verified = False,
                    google_oauth = False
                )
                asess.add(user)
                await asess.commit()
                self.set_signed_cookie("app_cookie", str(user.id))
                token = await ioloop.IOLoop.current().run_in_executor(None, generate_verification_token, email)
                verification_link = f'http://localhost:8888/verify?token={token}'
                await send_verification_email(email, verification_link)
                self.redirect('/')

class UserLoginHandler(BaseHandler):
    def get(self):
        '''
        If the user already logged in, redirect him to the homepage.
        '''
        self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.render('user/login.html')

    async def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        async with self.application.asession() as sess:
            query = select(User).where(User.username == username)
            result = await sess.execute(query)
            user = result.scalar_one_or_none()

        if not user:
            self.redirect('/auth/login')
            return

        password_check = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.checkpw,
            tornado.escape.utf8(password),
            tornado.escape.utf8(user.password)
        )
        if password_check:
            self.set_signed_cookie('app_cookie', str(user.id))
            self.redirect('/')
        else:
            self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.redirect('/auth/login')

class UserLogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie('app_cookie')
        self.redirect('/auth/login')

class UserProfileHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, user_id:int, username:str):
        async with self.application.asession() as sess:
            # Eagerly load topics and comments
            stmt = (
                select(User)
                .options(selectinload(User.topics), selectinload(User.comments).selectinload(Comment.topic))
                .where(User.id == user_id)
            )
            result = await sess.execute(stmt)
            user = result.scalar_one_or_none()

        if not user:
            self.send_error(404, reason="User not found.")
            return

        is_own_profile = self.current_user.id == int(user_id)

        self.render(
            "user/profile.html",
            profile_user=user,
            topics=user.topics,
            comments=user.comments,
            is_own_profile=is_own_profile
        )

class FetchUserPostsHandler(BaseHandler):
    async def get(self, user_id):
        stmt = select(Topic.id, Topic.title).where(Topic.user_id == int(user_id))
        async with self.application.asession() as session:
            results = await session.execute(stmt)
            topics = results.mappings().all()
        topics = [dict(topic) for topic in topics]
        self.set_header('Content-Type', 'application/json')
        self.write({'topics':topics})

class FetchUserCommentsHandler(BaseHandler):
    async def get(self, user_id:int):
        stmt = select(Comment).where(Comment.user_id == int(user_id))
        async with self.application.asession() as session:
            results = await session.execute(stmt)
            comments = results.scalars().all()
        comments = [{'id':comment.id, 'content':comment.content} for comment in comments]
        self.set_header('Content-Type', 'application/json')
        self.write({'comments': comments})

class FetchUserUpVotedPosts(BaseHandler):
    async def get(self, user_id:int):
        stmt = select(Topic)\
                .join(VoteTopic, VoteTopic.topic_id == Topic.id)\
                .where(VoteTopic.user_id == int(user_id))\
                .where(VoteTopic.vote_type == VoteType.UPVOTE)
        
        async with self.application.asession() as session:
            results = await session.execute(stmt)
            upvoted_topics = results.scalars().all()
        upvoted_topics = [{'id':topic.id, 'title':topic.title} for topic in upvoted_topics]
        self.set_header('Content-Type', 'application/json')
        self.write({'upvotedTopics': upvoted_topics})

class FetchUserDownVotedPosts(BaseHandler):
    async def get(self, user_id:int):
        stmt = select(Topic)\
                .join(VoteTopic, VoteTopic.topic_id == Topic.id)\
                .where(VoteTopic.user_id == int(user_id))\
                .where(VoteTopic.vote_type == VoteType.DOWNVOTE)
        
        async with self.application.asession() as session:
            results = await session.execute(stmt)
            downvoted_topics = results.scalars().all()
        downvoted_topics = [{'id':topic.id, 'title':topic.title} for topic in downvoted_topics]
        self.set_header('Content-Type', 'application/json')
        self.write({'downvotedTopics': downvoted_topics})

class SendVerificationMail(BaseHandler):
    async def post(self):
        data = json.loads(self.request.body)
        user_id = data.get('user_id', 0)
        self.set_header('Content-Type', 'application/json')
        async with self.application.asession() as sess:
            stmt = select(User).where(User.id == user_id)
            results = await sess.execute(stmt)
            user:User = results.scalar_one_or_none()
        if user:
            token = await ioloop.IOLoop.current().run_in_executor(None, generate_verification_token, user.email)
            verification_link = f'http://localhost:8888/verify?token={token}'
            email_sent = await send_verification_email(user.email, verification_link)
            if email_sent:
                self.set_status(200)
                self.write({'status':'ok', 'message':'Verification Email Successfully Sent'})
            else:
                self.set_status(500)
                self.write({'status':'error', 'message':'There is an error in sending the Verification email, please try after some time.'})


class EmailVerificationHandler(BaseHandler):
    async def get(self):
        token = self.get_query_argument('token', '', strip=True)
        if token:
            confirmation = await ioloop.IOLoop.current().run_in_executor(None, confirm_verification_token, token)
            if confirmation is not None:
                async with self.application.asession() as sess:
                    stmt = select(User).where(User.email == confirmation)
                    results = await sess.execute(stmt)
                    user = results.scalar_one_or_none()

                    if user:
                        user.email_verified = True
                        await sess.flush()
                        await sess.commit()
                    else:
                        print('User not found')
        if token and user:
            self.redirect('/')