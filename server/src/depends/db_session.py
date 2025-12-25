from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncSession:
    async with request.app.state.db_session_factory() as db_session:
        # must be used as 'async with db_session.begin():'
        yield db_session
