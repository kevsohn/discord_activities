from fastapi import Depends
import json
from redis.asyncio import Redis

from ..config import SESSION_TTL
from ..services.error import error
from .redis import get_redis


def get_state_cache(redis=Depends(get_redis)):
    return GameStateCache(redis)


class GameStateCache:
    def __init__(self, redis: Redis):
        self.redis = redis


    def _key(self, user_id: str, game_id: str) -> str:
        return f'game:{user_id}:{game_id}'


    async def store(self, user_id: str, game_id: str,
                  state: dict,
                  ttl: int = SESSION_TTL):
        '''
        Stores the game state in redis.
        state must be JSON-serializable.
        '''
        await self.redis.set(
                self._key(user_id, game_id),
                json.dumps(state),
                ex=ttl
        )


    async def get(self, user_id: str, game_id: str) -> dict:
        '''
        Returns game state.
        '''
        state = await self.redis.get(self._key(user_id, game_id))
        if state is None:
            raise error(404, 'Game not started')

        # redis.asyncio returns bytes so decode
        if isinstance(state, bytes):
            state = state.decode('utf-8')

        return json.loads(state)


    async def delete(self, user_id: str, game_id: str) -> bool:
        '''
        Deletes game state from redis.
        Returns True if existed and deleted.
        '''
        # returns nkeys deleted
        nkeys = await self.redis.delete(self._key(user_id, game_id))
        return nkeys > 0

