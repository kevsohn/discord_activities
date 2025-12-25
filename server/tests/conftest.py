import pytest
import pytest_asyncio
from fastapi import FastAPI
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from fakeredis import FakeAsyncRedis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from server.src.main import app
from server.src.db.models.stats import Base
from server.src.depends.db_session import get_db_session
from server.src.depends.redis import get_redis
from server.src.depends.http import get_http_client

pytestmark = pytest.mark.anyio(backend="asyncio")


@pytest_asyncio.fixture
async def game_id():
    return 'chess_puzzle'


@pytest_asyncio.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_db",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    #await engine.dispose()


@pytest_asyncio.fixture
async def db_session_factory(db_engine):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    yield factory


@pytest_asyncio.fixture
async def redis_client():
    redis = FakeAsyncRedis()
    yield redis
    #await redis.aclose()


@pytest_asyncio.fixture
async def http_client():
    http_client = AsyncClient(timeout=10)
    yield http_client
    #await http_client.aclose()


@pytest_asyncio.fixture
async def client(redis_client, db_engine, db_session_factory, http_client):
    async with LifespanManager(app):
        app.state.db_engine = db_engine
        app.state.db_session_factory = db_session_factory
        app.state.redis = redis_client
        app.state.http = http_client

        async def _get_db_session():
            async with app.state.db_session_factory() as db_session:
                yield db_session

        app.dependency_overrides[get_db_session] = _get_db_session
        app.dependency_overrides[get_redis] = lambda: redis_client
        app.dependency_overrides[get_http_client] = lambda: http_client

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as test_client:
            yield test_client

    # allow main.py to close conns before null
    app.state.http = None
    app.state.redis = None
    app.state.db_session = None
    app.state.db = None
    app.dependency_overrides.clear()


