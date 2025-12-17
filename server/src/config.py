from os import environ
from dotenv import load_dotenv
from engines.chess_puzzles import ChessPuzzleEngine
from engines.minesweeper import MinesweeperEngine
from services.lichess import fetch_daily_puzzle

# exports .env vars
load_dotenv()

# discord
CLIENT_ID = environ.get('CLIENT_ID')
CLIENT_SECRET = environ.get('CLIENT_SECRET')
DISCORD_API_URL = "https://discord.com/api/v10"

REDIS_URL = ''
DB_URL = ''

SESSION_TTL = 60*60*24  # session timeout every 24h

GAMES = {
    'chess': {
        'engine': ChessPuzzleEngine,
        'provider': fetch_daily_puzzle,
    },
    'minesweeper': {
        'engine': MinesweeperEngine,
        'provider': None,
    },
}
