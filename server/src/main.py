from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from shared.game_reg import GAMES
from server.src.config import REQUEST_TIMEOUT, REDIS_HOST, REDIS_PORT, DB_URL
from server.src.depends.engine_reg import init_game_engine

from server.src.api.auth import router as auth_router
from server.src.api.games import router as games_router
from server.src.api.stats import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Server starting up...')

    app.state.db_engine = create_async_engine(
        DB_URL,
        pool_pre_ping=True,  # pre-ping to check conn is alive
        echo=False,  # dont echo all queries
    )
    app.state.db_session_factory = async_sessionmaker(
        app.state.db_engine,
        expire_on_commit=False,  # persist conn after commit
    )
    print('DB startup: OK')

    app.state.redis = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,  # db number (0-16)
        decode_responses=True,  # retrn strings instead of bytes
    )
    print('Redis startup: OK')

    app.state.http = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    print('HTTP client startup: OK')

    app.state.engines = {}
    for game_id in GAMES:
        engine = await init_game_engine(game_id, app)
        app.state.engines[game_id] = engine
    print('Game Engines initialized')

    yield
    print('Server shutting down...')

    await app.state.http.aclose()
    print('HTTP client shutdown')
    await app.state.redis.aclose()
    print('Redis shutdown')
    await app.state.db_engine.dispose()
    print('DB shutdown')


# -------------- main -----------------
app = FastAPI(title="Discord Activities API", lifespan=lifespan)

# runs around every request (before/after)
# apparently needed for Discord iframe
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #["https://discord.com","https://*.discordsays.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(games_router)
app.include_router(stats_router)


