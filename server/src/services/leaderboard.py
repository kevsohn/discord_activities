from fastapi import FastAPI as app


async def rank_player(game_id: str,
                      user_id: str,
                      epoch: str,
                      score: int):
    redis = app.state.redis
    key = f'game:{game_id}:leaderboard:{epoch}'

    # only update if better score
    prev = await redis.zscore(key, user_id)
    if prev is not None and prev >= score:
        return

    await redis.zadd(key, {user_id: score})

