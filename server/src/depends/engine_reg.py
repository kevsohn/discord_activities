'''
All engines are initialized and stored in app.state.engines.

Follows a Singleton pattern since engines are state-agnostic:
Player states/game are stored in redis and loaded into engine on update call.

This way, frontend can swap games w/o reloading backend.
'''
from fastapi import FastAPI, Request, Path

from ..services.error import error
from ..engines.base import GameEngine
from ..engines.chess_puzzle import ChessPuzzleEngine
from ..engines.minesweeper import MinesweeperEngine
from ..providers.lichess import fetch_daily_puzzle


GAME_SPECS = {
    'chess_puzzle': {
        'engine': ChessPuzzleEngine,
        'provider': fetch_daily_puzzle,
    },
    'minesweeper': {
        'engine': MinesweeperEngine,
        'provider': None,
    },
}


# called by main.py @asynccontextmanager
async def init_game_engine(game_id: str, app: FastAPI) -> GameEngine:
    spec = GAME_SPECS.get(game_id)
    if not spec:
        raise error(404, f'Unknown game: {game_id}')

    engine_cls = spec['engine']
    provider = spec['provider']

    # if game doesnt need external data
    if provider is None:
        return engine_cls()

    fetcher = lambda: provider(app.state.http)
    return engine_cls(fetcher)


# called by api/games route
async def get_game_engine(request: Request,
                          game_id: str = Path(...)) -> GameEngine:
    '''
    Receives game_id from frontend route,
    returns the appropriate game engine.
    '''
    # use .get() to avoid KeyError
    engine = request.app.state.engines.get(game_id)
    if not engine:
        raise error(404, f'Unknown game: {game_id}')
    return engine


