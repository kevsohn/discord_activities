from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.stats import Stats
from ..depends.db_session import get_db_session
from ..services.error import error

router = APIRouter(prefix='/api/stats')


# Mainly for discord bot, so no session id block
@router.get('/{game_id}/daily')
async def daily_stats(game_id: str,
                      db_session: AsyncSession=Depends(get_db_session)) -> dict:
    '''
    Returns daily stats for requested game.
    '''
    async with db_session.begin():
        res = await db_session.execute(
            select(Stats)
            .where(Stats.game_id == game_id)
            .order_by(Stats.date.desc())
            .limit(1)
        )
        stats = res.scalar_one_or_none()
        if stats is None:
            raise error(404, f'Stats not found for {game_id}')

        return {
            'date': stats.date.date(),
            'rankings': stats.rankings,
            'max_score': stats.max_score,
            'streak': stats.streak,
        }
