import redis.asyncio as Redis


async def rank_player(game_id: str,
                      user_id: str,
                      epoch: str,
                      score: int,
                      redis: Redis):
    key = f'game:{game_id}:leaderboard:{epoch}'
    # game could prio lower scores or higher scores,
    # so no preferential adding
    await redis.zadd(key, {user_id: score})

