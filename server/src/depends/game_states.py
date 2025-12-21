from fastapi import Depends
import json
from redis.asyncio import Redis

from .redis import get_redis


def get_state_store(redis=Depends(get_redis)):
    return GameStateStore(redis)


class GameStateStore:
    def __init__(self, redis: Redis):
        self.redis = redis


    def _key(self, game_id: str, user_id: str, epoch: str) -> str:
        return f'game:{game_id}:{user_id}:{epoch}'


    async def store(self,
                    game_id: str,
                    user_id: str,
                    epoch: str,
                    state: dict,
                    ttl: int):
        '''
        Stores the game state in redis.
        state must be JSON-serializable.
        '''
        await self.redis.set(
                self._key(game_id, user_id, epoch),
                json.dumps(state),
                ex=ttl
        )


    async def get(self, game_id: str, user_id: str, epoch: str) -> dict:
        '''
        Returns game state.
        '''
        state = await self.redis.get(self._key(game_id, user_id, epoch))
        if state is None:
            return None

        # redis.asyncio returns bytes so decode
        if isinstance(state, bytes):
            state = state.decode('utf-8')

        return json.loads(state)


    async def delete(self, game_id: str, user_id: str, epoch: str) -> bool:
        '''
        Deletes game state from redis.
        Returns True if existed and deleted.
        '''
        # returns nkeys deleted
        nkeys = await self.redis.delete(self._key(game_id, user_id, epoch))
        return nkeys > 0

