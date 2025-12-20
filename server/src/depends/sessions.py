from fastapi import Request, Depends
import json
from redis.asyncio import Redis

from ..config import SESSION_TTL
from ..services.error import error
from .redis import get_redis


def get_session_id(request: Request):
    session_id = request.cookies.get('session_id')
    if not session_id:
        raise error(401, 'User not authenticated')
    return session_id


def get_session_manager(redis=Depends(get_redis)):
    return SessionManager(redis)


class SessionManager:
    '''Redis interface for sessions.'''
    def __init__(self, redis: Redis):
        self.redis = redis


    def _key(self, session_id: str) -> str:
        return f'session:{session_id}'


    async def create(self, session_id: str, user_data: dict, ttl: int = SESSION_TTL):
        '''
        Creates a new session in redis.
        user_data must be JSON-serializable.
        '''
        await self.redis.set(
                self._key(session_id),
                json.dumps(user_data),
                ex=ttl
        )


    async def get(self, session_id: str) -> dict:
        '''
        Returns session data.
        '''
        data = await self.redis.get(self._key(session_id))
        if data is None:
            raise error(401, 'User not authenticated')

        # redis.asyncio returns bytes so decode
        if isinstance(data, bytes):
            data = data.decode('utf-8')

        return json.loads(data)


    async def delete(self, session_id: str) -> bool:
        '''
        Deletes a session from redis.
        Returns True if session existed and was deleted.
        '''
        # returns nkeys deleted
        nkeys = await self.redis.delete(self._key(session_id))
        return nkeys > 0


