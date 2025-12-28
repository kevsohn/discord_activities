from fastapi import Request, Depends
import json
from redis.asyncio import Redis

from ..config import SESSION_TTL
from .redis import get_redis
from ..services.error import error


def get_session_id(request: Request):
    session_id = request.cookies.get('session_id')
    if not session_id:
        raise error(401, 'User not authenticated')
    return session_id


def get_session_manager(redis=Depends(get_redis)):
    return SessionManager(redis)


class SessionManager:
    '''Redis interface for sessions.'''
    def __init__(self, redis: Redis, ttl=SESSION_TTL):
        self.redis = redis
        self.ttl = ttl


    def _key(self, session_id: str) -> str:
        return f'session:{session_id}'


    async def create(self,
                     session_id: str,
                     user_id: str,
                     ttl: int | None = None):
        '''
        Create a new session.
        user_data must be JSON-serializable.
        '''
        # if ttl is not None, it is truthy so short circuit
        ttl = ttl or self.ttl

        await self.redis.set(
                self._key(session_id),
                json.dumps({'user_id': user_id}),
                ex=ttl
        )


    async def get(self, session_id: str) -> dict | None:
        '''Fetches session and refresh TTL.'''
        key = self._key(session_id)
        uid = await self.redis.get(key)
        if uid is None:
            return None

        # sliding expiary: if exists, extend ttl
        await self.redis.expire(key, self.ttl)

        # redis.asyncio returns bytes so decode
        if isinstance(uid, bytes):
            uid = uid.decode('utf-8')

        return json.loads(uid)


    async def delete(self, session_id: str) -> bool:
        '''
        Deletes a session from redis.
        Returns True if session existed and was deleted.
        '''
        # returns nkeys deleted
        nkeys = await self.redis.delete(self._key(session_id))
        return nkeys > 0


