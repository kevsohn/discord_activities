from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db(request: Request) -> AsyncSession:
    '''User must start w/ async with db.begin():'''
    async with request.app.state.db_session as db:
        yield db
