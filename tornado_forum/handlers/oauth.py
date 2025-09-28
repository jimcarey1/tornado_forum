#This entire code snippet copied from the (https://www.tornadoweb.org/en/stable/auth.html)
import tornado
import urllib
from sqlalchemy import select

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
            print(f'The user is {user}')
            username = user['id']
            email = user['email']
            password = generate_random_string(10)
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
            self.redirect("/")
        else:
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=self.get_google_oauth_settings()["key"],
                scope=["openid", "profile", "email"],
                response_type="code",
                extra_params={"approval_prompt": "auto"},
            )