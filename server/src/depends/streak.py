from fastapi import Depends

from .redis import get_redis
from ..services.reset import get_current_epoch, seconds_til_next_reset


# called in api/stats
async def incr_streak(game_id: str, redis=Depends(get_redis)):
    '''
    Increment streak once if anyone played this epoch
    '''
    epoch = get_current_epoch()
    # if none played, return
    if not await any_user_played(game_id, epoch, redis):
        return

    # key to guard against multiple increments.
    guard_key = f'game:{game_id}:played:{epoch}'
    ttl = seconds_til_next_reset()
    # setnx returns True if key was created and
    # False if key already exists,
    # so return if key already exists since someone
    # has already played this epoch.
    if not await redis.set(guard_key, 1, nx=True, ex=ttl):
        return

    key = f'game:{game_id}:streak'
    await redis.incr(key)


# helper fn
async def any_user_played(game_id: str, epoch: str, redis) -> bool:
    '''
    Returns True if any user has a game state key this epoch
    '''
    pattern = f"game:{game_id}:*:{epoch}"
    # redis.asyncio scan is safe for async, avoids blocking
    cursor = 0
    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match=pattern,
            count=1  # scans upto 1 key
        )
        if keys:
            return True
        if cursor == 0:  # cursor resets to 0 when scan complete
            break
    return False


