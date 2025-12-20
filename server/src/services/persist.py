from sqlalchemy.ext.asyncio import AsyncSession


def save_score(db: AsyncSession,
               game_id: str,
               user_id: str,
               score: int):
    #async with db.begin():
    #    db.add()
    pass
