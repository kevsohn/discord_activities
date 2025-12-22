from datetime import datetime
import redis.asyncio as Redis
from sqlalchemy.ext.asyncio import AsyncSession

from shared.game_reg import GAMES
from ..db.models.stats import Stats


# called by GameEngine().ensure_reset()
async def save_stats(game_id: str,
                     prev_epoch: str,
                     max_score: int,
                     redis: Redis,
                     db_session: AsyncSession):
    '''
    Saves game stats after daily reset.
    '''
    # increment streak after reset if requirements met
    await incr_streak(game_id, prev_epoch, redis)
    streak = await redis.get(f'game:{game_id}:streak')

    leaderboard_key = f'game:{game_id}:leaderboard:{prev_epoch}'
    order = GAMES[game_id]['rank_order']
    if order not in ('asc', 'desc'):
        raise error(401, 'Invalid rank order')

    if order == 'asc':
        rankings = await redis.zrange(
            leaderboard_key, 0, -1, withscores=True
        )
    else:
        rankings = await redis.zrevrange(
            leaderboard_key, 0, -1, withscores=True
        )

    # to make output JSON-serializable
    rankings_list = [
        {'user_id': user_id.decode('utf-8'), 'score': int(score)}
        for user_id, score in rankings
    ]

    stats = Stats(
        game_id=game_id,
        date=epoch_to_datetime(prev_epoch),
        rankings=rankings_list,
        max_score=max_score,
        streak=int(streak) if streak else 0
    )

    async with db_session as db:
        async with db.begin():
            db.add(stats)

    # del after saving in case db fails
    # delete yesterday's stats since no TTL
    guard_key = f'game:{game_id}:played:{prev_epoch}'
    await redis.delete(guard_key)
    await redis.delete(leaderboard_key)


def epoch_to_datetime(epoch: str) -> datetime:
    date, hour = epoch.split('@')
    return datetime.fromisoformat(date).replace(
        hour=int(hour),
        minute=0,
        second=0,
        microsecond=0
    )

