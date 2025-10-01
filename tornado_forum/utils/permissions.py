from typing import Callable, Optional, Awaitable
import functools
from tornado.web import HTTPError, RequestHandler

def is_admin(
        method: Callable[..., Optional[Awaitable[None]]]
)->Callable[..., Optional[Awaitable[None]]]:
    @functools.wraps(method)
    def wrapper(self:RequestHandler, *args, **kwargs):
        if not self.current_user.is_admin:
            raise HTTPError(403, 'Forbidden')
        return method(self, *args, **kwargs)
    return wrapper

def can_change_username(method: Callable[..., Optional[Awaitable[None]]]) -> Callable[..., Optional[Awaitable[None]]]:
    @functools.wraps(method)
    def wrapper(self:RequestHandler, *args, **kwargs):
        if not self.current_user.can_change_username:
            raise HTTPError(403, 'Forbidden')
        return method(self, *args, **kwargs)
    return wrapper

def is_owner_or_admin(
        method: Callable[..., Optional[Awaitable[None]]]
)->Callable[..., Optional[Awaitable[None]]]:
    @functools.wraps(method)
    def wrapper(self:RequestHandler, *args, **kwargs):
        #do something here
        return method(self, *args, **kwargs)
    return wrapper

