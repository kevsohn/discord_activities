from fastapi import Request, Depends

from ..services.sessions import SessionManager
from .redis import get_redis


def get_session_manager(redis=Depends(get_redis)):
    return SessionManager(redis)


def get_session_id(request: Request):
    session_id = request.cookies.get('session_id')
    if not session_id:
        raise error(401, 'User not authenticated')
    return session_id

