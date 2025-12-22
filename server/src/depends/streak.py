from fastapi import Depends
from redis.asyncio import Redis

from .redis import get_redis
from ..services.reset import get_current_epoch


# called in api/games at every game start
async def mark_played(game_id: str, redis=Depends(get_redis)):
    '''
    Mark if the game has been played today.
    '''
    epoch = get_current_epoch()

    guard_key = f'game:{game_id}:played:{epoch}'
    # set guard key only on first play of the day.
    # True if guard key has been set today
    if not await redis.set(guard_key, 1, nx=True):
        return

    # if first play of day, update last played epoch to now
    await redis.set(f'game:{game_id}:last_played_epoch', epoch)


# called in services.save
async def incr_streak(game_id: str, prev_epoch: str, redis: Redis):
    '''
    Increment streak if played on consecutive days.
    '''
    #assert prev_epoch is not None
    streak_key = f'game:{game_id}:streak'
    last_played = await redis.get(f'game:{game_id}:last_played_epoch')

    # if last played == yesterday, then incr else reset
    if last_played == prev_epoch:
        await redis.incr(streak_key)
    else:
        await redis.set(streak_key, 0)
