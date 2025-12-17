from engines.chess_puzzles import ChessPuzzleEngine
from engines.minesweeper import MinesweeperEngine
from services.lichess import fetch_daily_puzzle

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
