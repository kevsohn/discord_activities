from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import redis.asyncio as redis

from shared.game_reg import GAMES
from server.src.config import REQUEST_TIMEOUT, REDIS_HOST, REDIS_PORT
from server.src.depends.engine_reg import init_game_engine

from server.src.api.games import router as games_router
from server.src.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Server starting up...')
    app.state.http = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    app.state.redis = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True,  # retrn strings instead of bytes
    )
    #app.state.db = psycopg2.connect(url=DB_URL)

    app.state.engines = {}
    for game_id in GAMES:
        engine = await init_game_engine(game_id, app)
        app.state.engines[game_id] = engine

    '''
    scheduler = AsyncIOScheduler()
    async def check_reset_time():
        now = datetime.utcnow()
        reset_t = app.state.db.get_reset_time()
        if now >= reset_t:
            app.state.db.set_reset_time(reset_t + timedelta(hour=24))
    scheduler.add_job(check_reset_time, 'interval', hours=1)
    scheduler.start()
    app.state.scheduler = scheduler
    '''

    yield
    print('Server shutting down...')
    await app.state.http.aclose()
    await app.state.redis.close()
    #await app.state.db.close()


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

app.include_router(games_router)
app.include_router(auth_router)


