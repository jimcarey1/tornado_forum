from typing import Callable, Optional, Awaitable
import functools
from tornado.web import HTTPError, RequestHandler

def is_admin(
        method: Callable[..., Optional[Awaitable[None]]]
)->Callable[..., Optional[Awaitable[None]]]:
    @functools.wraps(method)
    def wrapper(self:RequestHandler, *args, **kwargs):
        if not self.current_user.is_admin:
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper