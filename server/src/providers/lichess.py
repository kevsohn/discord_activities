'''
Data provider for ChessPuzzleEngine.
'''
import io
import chess.pgn

from ..services.error import error

LICHESS_API_URL = "https://lichess.org/api"


# http_client is currently httpx.AsyncClient but can be swapped
async def fetch_daily_puzzle(http_client) -> dict:
    '''Returns the daily puzzle in FEN format.'''
    data = fetch_lichess_puzzle(http_client)

    pgn = data['game']['pgn']
    init_ply = data['puzzle']['initialPly']
    fen = pgn_to_fen(pgn, init_ply)

    return {
        'fen': fen,
        'solution': data['puzzle']['solution'],
    }


async def fetch_puzzle_metadata(http_client) -> dict:
    data = fetch_lichess_puzzle(http_client)
    rating = data['puzzle']['rating']
    return {
        'rating': rating
    }


async def fetch_lichess_puzzle(http_client) -> dict:
    '''Returns the lichess daily puzzle.'''
    r = await http_client.get(f'{LICHESS_API_URL}/puzzle/daily')
    if r.status_code != 200:
        raise error(r.status_code, 'Failed to fetch daily chess puzzle')

    return r.json()


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



