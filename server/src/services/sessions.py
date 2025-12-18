import json
from redis.asyncio import Redis
from secrets import token_urlsafe

from ..config import SESSION_TTL
from .error import error


class SessionManager:
    def __init__(self, redis: Redis, ttl: int = SESSION_TTL):
        self.redis = redis
        self.ttl = ttl


    async def create(self, data: dict) -> str:
        '''
        Creates a new session in redis and returns session id.
        data must be JSON-serializable.
        '''
        session_id = token_urlsafe(32)
        await self.redis.set(
                f'session:{session_id}',
                json.dumps(data),
                ex=self.ttl
        )
        return session_id


    async def get(self, session_id: str, key: str | None = None):
        '''
        Retrieves a session from redis. Raises 404 if not found.
        Returns entire dict if no key specified.
        '''
        session = await self.redis.get(f'session:{session_id}')
        if session is None:
            raise error(404, 'User not authenticated')

        # redis.asyncio returns bytes so decode
        if isinstance(session, bytes):
            session = session.decode('utf-8')

        data = json.loads(session)
        return data if key is None else data.get(key)


    async def delete(self, session_id: str) -> bool:
        '''
        Deletes a session from redis.
        Returns True if session existed and was deleted.
        '''
        # returns nkeys deleted
        nkeys = await self.redis.delete(f'session:{session_id}')
        return nkeys > 0


