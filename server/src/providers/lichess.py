'''
Data provider for ChessPuzzleEngine.
'''
import chess
import chess.pgn
import io

from ..services.error import error
from ..config import LICHESS_SECRET, b_TEST


TEST_URL = "https://lichess.org/api/puzzle/00sJ9"
API_URL = "https://lichess.org/api/puzzle/daily"
#API_URL = "https://lichess.org/api/puzzle/next"


# http_client is currently httpx.AsyncClient but can be swapped
async def fetch_daily_puzzle(http_client) -> dict:
    '''
    Returns the lichess daily puzzle.
    '''
    headers={
        "Authorization": f"Bearer {LICHESS_SECRET}"
    }
    params={
        "angle": "",
        "difficulty": "normal",
        "color": ""   # 50% w or b
    }

    if b_TEST:
        r = await http_client.get(TEST_URL)
    else:
        r = await http_client.get(
            API_URL,
            #headers=headers,
            #params=params
        )

    if r.status_code != 200:
        raise error(r.status_code, 'Failed to fetch daily chess puzzle')
    data = r.json()

    # check lichess api docs
    pgn = data['game']['pgn']
    init_ply = data['puzzle']['initialPly']
    rating = data['puzzle']['rating']
    solution = data['puzzle']['solution']

    fen = pgn_to_fen(pgn, init_ply)
    print(fen, solution, rating)

    return {
        'fen': fen,
        'solution': solution,  # UCI
        'rating': rating
    }


def pgn_to_fen(pgn: str, init_ply: int) -> str:
    '''
    convert Portable-Game -> Forsynth-Edwards
    '''
    pgn_obj = chess.pgn.read_game(io.StringIO(pgn))
    board = pgn_obj.board()

    # play moves up to init ply
    for ply, move in enumerate(pgn_obj.mainline_moves()):
        board.push(move)
        if ply == init_ply:
            break

    return board.fen()


