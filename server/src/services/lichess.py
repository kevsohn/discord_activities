import httpx
import io
import chess.pgn

from ..config import LICHESS_API_URL
from .error import error


async def fetch_daily_puzzle(http: httpx.AsyncClient) -> dict:
    '''
    Returns the lichess daily puzzle in FEN format for ChessPuzzleEngine.
    '''
    r = await http.get(f'{LICHESS_API_URL}/puzzle/daily')
    if r.status_code != 200:
        raise error(r.status_code, 'Failed to fetch daily chess puzzle')

    data = r.json()
    pgn = data['game']['pgn']
    init_ply = data['puzzle']['initialPly']
    fen = pgn_to_fen(pgn, init_ply)

    return {
        'fen': fen,
        'solution': data['puzzle']['solution'],
        'rating': data['puzzle']['rating']
    }


def pgn_to_fen(pgn: str, initial_ply: int) -> str:
    '''
    i.e. full game history -> specific game position.
    A "ply" is a single move by one player (half-move).
    '''
    game = chess.pgn.read_game(io.StringIO(pgn))
    board = game.board()

    for i, move in enumerate(game.mainline_moves()):
        if i == initial_ply:  # ply is 0-indexed like i
            break
        board.push(move)

    return board.fen()

