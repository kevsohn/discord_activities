from fastapi import FastAPI as app

import json


# called by GameEngine().ensure_reset()
async def save_stats(game_id: str, prev_epoch: str, max_score: int):
    '''Saves game stats after daily reset.'''
    redis = app.state.redis

    # increment streak after reset if requirements met
    await incr_streak(game_id, prev_epoch, redis)

    streak_key = f'game:{game_id}:streak'
    leaderboard_key = f'game:{game_id}:leaderboard:{prev_epoch}'

    streak = await redis.get(streak_key)
    rankings = await redis.get(leaderboard_key)

    # sqlalchemy model
    stats = {
        'game_id': game_id,
        'date': prev_epoch[:-3],  # epoch: YYYY-MM-DD@HH
        'streak': int(streak) if streak else 0,
        'rankings': json.loads(rankings) if rankings else [],
        'max_score': max_score,
    }

    async with app.state.db_session as db:
        async with db.begin():
            db.add(stats)

    # del after saving in case db fails
    # delete yesterday's stats since no TTL
    guard_key = f'game:{game_id}:played:{epoch}'
    await redis.delete(guard_key)
    await redis.delete(leaderboard_key)

