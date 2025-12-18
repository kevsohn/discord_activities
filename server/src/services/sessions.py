'''
Module for con(de)structing sessions.
Getting session_ids and user_id is done thru Depends.
'''
from secrets import token_urlsafe

from ..config import SESSION_TTL
from .error import error


async def create_session(user_id: str, redis) -> str:
    '''
    Stores user in a Redis and returns session id
    '''
    session_id = token_urlsafe(32)
    await redis.set(
        f'session:{session_id}',
        user_id,  # change to user_info if needed
        ex=SESSION_TTL
    )
    return session_id


async def delete_session(session_id: str, redis):
    await redis.delete(f'session:{session_id}')


