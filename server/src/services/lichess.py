import requests
import chess.pgn
import io


URL = r"https://lichess.org/api/puzzle/daily"


def fetch_daily_puzzle() -> dict:
    r = requests.get(URL)
    r.raise_for_status()
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
        if i == initial_ply:
            break
        board.push(move)

    return board.fen()

