import pytest_asyncio
from fakeredis import FakeAsyncRedis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from server.src.main import app


@pytest_asyncio.fixture
async def game_id():
    return 'chess_puzzle'


@pytest_asyncio.fixture
async def redis_client():
    redis = FakeAsyncRedis()
    yield redis
    await redis.aclose()


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_db",
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with db_engine.begin() as conn:
        async with Session(bind=conn) as session:
            yield session
            await conn.rollback()


@pytest_asyncio.fixture
async def client(redis_client, db_session):
    app.state.redis = redis_client
    app.state.db_session = db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.state.redis = None
    app.state.db_session = None
    app.dependency_overrides.clear()


