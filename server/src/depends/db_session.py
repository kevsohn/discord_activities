from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


def get_db_session(request: Request):
    async with request.app.state.db_session as db:
        yield db
