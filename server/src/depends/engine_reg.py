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

ENGINES = {
    'chess_puzzle': {
        'engine': ChessPuzzleEngine,
        'provider': fetch_daily_puzzle,
    },
    'minesweeper': {
        'engine': MinesweeperEngine,
        'provider': None,
    },
}


# called by api/games
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


# called by main.py @asynccontextmanager so no Depends()
async def init_game_engine(game_id: str, app: FastAPI) -> GameEngine:
    engine = ENGINES.get(game_id)
    if not engine:
        raise error(404, f'Unknown game: {game_id}')

    engine_cls = engine['engine']
    provider = engine['provider']

    # if game doesnt need external data
    if provider is None:
        return engine_cls(game_id, app.state.redis, app.state.db_session)

    fetcher = lambda: provider(app.state.http)
    return engine_cls(game_id,
                      app.state.redis,
                      app.state.db_session,
                      fetcher)


