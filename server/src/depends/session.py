from fastapi import Request, Depends

from ..services.error import error
from .redis import get_redis


def get_session_id(request: Request) -> str:
    # cookies are created w/ sessions in api.auth
    session_id = request.cookies.get('session_id')
    if not session_id:
        raise error(401, "Not authenticated")
    return session_id


async def get_user_id(session_id=Depends(get_session_id),
                      redis=Depends(get_redis)) -> str:
    user_id = await redis.get(f'session:{session_id}')
    if not user_id:
        raise error(401, "Session expired or invalid")
    return user_id
