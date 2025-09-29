#This entire code snippet copied from the (https://www.tornadoweb.org/en/stable/auth.html)
import tornado
import urllib
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .base import BaseHandler
from models.user import User
from utils.generate_random_strings import generate_random_string

class GoogleOAuth2LoginHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
    async def get(self):
        redirect_uri = urllib.parse.urljoin(
            self.application.settings["redirect_base_uri"],
            self.reverse_url("google_oauth"),
        )
        if self.get_argument("code", False):
            access = await self.get_authenticated_user(
                redirect_uri=redirect_uri, code=self.get_argument("code")
            )
            user = await self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"],
            )
            username = user['id']
            email = user['email']
            password = generate_random_string(10)
            #We will check, if the user already registered, If he did we just set the cookie, else we will add him to db.
            async with self.application.asession() as sess:
                stmt = select(User).where(User.email == email)
                results = await sess.execute(stmt)
                user = results.scalar_one_or_none()
                if not user:
                    user = User(username=username, email=email, password=password, email_verified=True, google_oauth=True, access_token=access['access_token'])
                    sess.add(user)
                    await sess.commit()
            # Save the user and access token.
            #user_cookie = dict(id=user["id"], access_token=access["access_token"])
            self.set_signed_cookie("app_cookie", str(user.id))
            self.redirect(f"/change/username/{user.id}")
        else:
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=self.get_google_oauth_settings()["key"],
                scope=["openid", "profile", "email"],
                response_type="code",
                extra_params={"approval_prompt": "auto"},
            )

class ChangeUsernameHandler(BaseHandler):
    async def get(self):
        self.render('user/change_username.html')

    @tornado.web.authenticated
    async def post(self, user_id:int):
        username = self.get_argument('change-username', '').strip()
        confirm_username = self.get_argument('confirm-change-username', '').strip()
        if(username and confirm_username and username==confirm_username):
            async with self.application.asession() as sess:
                #Checking if the username is already taken or not.
                stmt = select(User.id).where(User.username == username)
                results = await sess.execute(stmt)
                user = results.scalar_one_or_none()

                if user:
                    self.set_status(409)
                    self.write({'error': 'Username already taken'})
                    return
                
                stmt = select(User).where(User.id == user_id)
                results = await sess.execute(stmt)
                user = results.scalar_one_or_none()
                if not user:
                    self.set_status(404)
                    self.write({'error': f'User with id: {user_id} not found.'})
                    return
                else:
                    user.username = username
                    try:
                        await sess.flush()
                        await sess.commit()
                    except IntegrityError:
                        await sess.rollback()
                        self.set_status(409)
                        self.write({'error': 'username already taken'})
                        return
                    except Exception as exc:
                        await sess.rollback()
                        self.set_status(500)
                        self.write({'error':'Internal Error', 'details': str(exc)})
                        return
                    
            self.set_status(200)
            self.write({'status':'ok', 'message':'Username changed successfully'})
                    
                