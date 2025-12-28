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
    '''
    Redis interface for sessions.
    '''
    def __init__(self, redis: Redis, ttl=SESSION_TTL):
        self.redis = redis
        self.ttl = ttl


    def _key(self, session_id: str) -> str:
        return f'session:{session_id}'


    async def create(self, session_id: str, user_id: str, ttl: int | None = None):
        '''
        Create a new session in redis.
        user_id must be JSON-serializable.
        '''
        # if ttl is not None, it is truthy so short circuit
        ttl = ttl or self.ttl

        await self.redis.set(
                self._key(session_id),
                json.dumps({'user_id': user_id}),
                ex=ttl
        )


    async def get(self, session_id: str) -> dict | None:
        '''
        Decodes and returns user_id from redis.
        '''
        key = self._key(session_id)
        user_id = await self.redis.get(key)
        if user_id is None:
            return None

        # redis.asyncio returns bytes so decode
        if isinstance(user_id, bytes):
            user_id = user_id.decode('utf-8')
        return json.loads(user_id)


    async def heartbeat(self, session_id: str):
        '''
        Extends session by self.ttl every heartbeat.
        '''
        key = self._key(session_id)
        if await self.redis.exists(key):
            await self.redis.expire(key, self.ttl)
            return True
        return False


