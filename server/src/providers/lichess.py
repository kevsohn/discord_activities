'''
Data provider for ChessPuzzleEngine.
'''
from ..services.error import error

API_URL = 'https://chess-puzzles.p.rapidapi.com/'
RATING = 1500


# http_client is currently httpx.AsyncClient but can be swapped
async def fetch_daily_puzzle(http_client) -> dict:
    '''
    Returns the lichess daily puzzle.
    '''
    headers = {
        "x-rapidapi-key": "577e35e7c9msh9808fce86f3b4aap1adf59jsne16c3a46b8cf",
        "x-rapidapi-host": "chess-puzzles.p.rapidapi.com"
    }
    params = {
        #'rating': f'{RATING}',
        #'count': '1',
        'id': 'HxxIU',  # for testing
    }

    r = await http_client.get(
        API_URL,
        headers=headers,
        params=params
    )
    if r.status_code != 200:
        raise error(r.status_code, 'Failed to fetch daily chess puzzle')
    data = r.json()

    puzzle = data['puzzles'][0]
    '''
    FEN is the position before the opponent makes their move.
    The position to present to the player is after applying the first move
    to that FEN. The second move is the beginning of the solution.
    '''
    return {
        'fen': puzzle['fen'],
        'moves': puzzle['moves'],  # UCI
        'rating': puzzle['rating']
    }

