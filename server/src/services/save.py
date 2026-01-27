from datetime import datetime
import redis.asyncio as Redis
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.dialects.postgresql import insert

from ..config import GAMES
from .error import error
from ..db.models.stats import Stats
from ..depends.streak import incr_streak


# called by GameEngine().ensure_reset()
async def save_stats_to_db(game_id: str,
                           prev_epoch: str,
                           outof: int,
                           redis: Redis,
                           db_session_factory: async_sessionmaker):
    '''
    Persist game stats after daily reset.
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

    # decode_responses=True in redis settings so technically dont need to decode
    rankings_list = [
        {'user_id': user_id.decode('utf-8') if isinstance(user_id, bytes) else user_id,
         'score': int(score)}
        for user_id, score in rankings
    ]

    stats = Stats(
        game_id=game_id,
        date=epoch_to_datetime(prev_epoch),
        rankings=rankings_list,
        outof=outof,
        streak=int(streak) if streak else 0
    )

    async with db_session_factory() as db_session:
        async with db_session.begin():
            stmt = insert(Stats).values(
                game_id=game_id,
                date=epoch_to_datetime(prev_epoch),
                rankings=rankings_list,
                outof=outof,
                streak=int(streak) if streak else 0,
            ).on_conflict_do_update(
                index_elements=[Stats.game_id],
                set_={
                    "date": epoch_to_datetime(prev_epoch),
                    "rankings": rankings_list,
                    "outof": outof,
                    "streak": int(streak) if streak else 0,
                },
            )
            await db_session.execute(stmt)

    # del after saving in case db fails
    # delete yesterday's stats since no TTL
    guard_key = f'game:{game_id}:played:{prev_epoch}'
    await redis.delete(guard_key)
    await redis.delete(leaderboard_key)


def epoch_to_datetime(epoch: str) -> datetime:
    return datetime.fromisoformat(epoch).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

