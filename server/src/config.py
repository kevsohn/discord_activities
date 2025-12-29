from os import environ
from dotenv import load_dotenv
from pathlib import Path
import json


# adjustable constants
GAME_RESET_HOUR = 0   # midnight UTC
SESSION_TTL = 60      # lifetime in secs >= 2x heartbeat
REQUEST_TIMEOUT = 10  # httpx client timeout in secs


# grab game specs
fpath = Path(__file__).resolve().parents[2] / "shared" / "game_reg.json"
with open(fpath, 'r') as f:
    specs = json.load(f)

GAMES = specs['games']


# export .env vars
load_dotenv()

# discord dev stuff
DISCORD_API_URL = "https://discord.com/api/v10"
CLIENT_ID = environ.get('CLIENT_ID')
CLIENT_SECRET = environ.get('CLIENT_SECRET')
REDIRECT_URI = environ.get('REDIRECT_URI')

REDIS_HOST = environ.get('REDIS_HOST')
REDIS_PORT = environ.get('REDIS_PORT')

DB_HOST = environ.get('DB_HOST')
DB_PORT = environ.get('DB_PORT')
DB_USER = environ.get('DB_USER')
DB_PWD =  environ.get('DB_PWD')
DB_NAME = environ.get('DB_NAME')
DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

