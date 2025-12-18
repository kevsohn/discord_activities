from os import environ
from dotenv import load_dotenv

load_dotenv()  # exports .env

SESSION_TTL = 3600    # session/redis time-to-live: 1h
REQUEST_TIMEOUT = 10  # httpx client timeout in secs

DISCORD_API_URL = "https://discord.com/api/v10"
LICHESS_API_URL = "https://lichess.org/api"

# discord dev stuff
CLIENT_ID = environ.get('CLIENT_ID')
CLIENT_SECRET = environ.get('CLIENT_SECRET')
REDIRECT_URI = environ.get('REDIRECT_URI')

REDIS_HOST = environ.get('REDIS_HOST')
REDIS_PORT = environ.get('REDIS_PORT')

#DB_HOST = environ.get('DB_HOST')
#DB_PORT = environ.get('DB_HOST')
#DB_NAME = environ.get('DB_NAME')
