#This entire code snippet copied from the (https://www.tornadoweb.org/en/stable/auth.html)
import tornado
import urllib

from .base import BaseHandler

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
            print(user)
            # Save the user and access token.
            #user_cookie = dict(id=user["id"], access_token=access["access_token"])
            self.set_signed_cookie("googledemo_user", str(user['id']))
            self.redirect("/")
        else:
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=self.get_google_oauth_settings()["key"],
                scope=["profile", "email"],
                response_type="code",
                extra_params={"approval_prompt": "auto"},
            )