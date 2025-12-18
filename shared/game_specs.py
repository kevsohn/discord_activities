'''
Specifications for hot-swappable discord activites
'''
from server.src.engines.chess_puzzles import ChessPuzzleEngine

GAMES = ['chess', 'minesweeper']

SPECS = {
    'chess': {
        'engine': ChessPuzzleEngine,
        'rank_order': 'desc',
    },
}
