from fastapi import Depends

from .redis import get_redis
from ..services.reset import get_current_epoch


async def rank(game_id: str, redis=Depends(get_redis)):
    epoch = get_current_epoch()
    key = f'game:{game_id}:*:{epoch}'
    pass

# persist rankings? reset rankings only after being called once? how does the bot know when to ask?
