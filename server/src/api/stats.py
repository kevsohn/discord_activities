from fastapi import APIRouter, Depends
import json

from ..depends.redis import get_redis


router = APIRouter(prefix='/api/stats')

@router.get('/{game_id}/streak')
async def streak(game_id: str, redis=Depends(get_redis)) -> int:
    key = f'game:{game_id}:streak'
    val = await redis.get(key)
    return int(val) if val else 0


@router.get('/{game_id}/leaderboard')
async def leaderboard(game_id: str, redis=Depends(get_redis)) -> dict:
    key = f'game:{game_id}:leaderboard'
    data = redis.get(key)
    if data is None:
        return {}
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    return json.loads(data)
