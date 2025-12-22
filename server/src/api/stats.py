from fastapi import APIRouter, Depends
import json

from ..depends.redis import get_redis

router = APIRouter(prefix='/api/stats')


@router.get('/{game_id}/stats')
async def stats(game_id: str) -> dict:
    # fetch from db
    pass
