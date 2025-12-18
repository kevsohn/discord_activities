'''
Game logic interface for the frontend
'''
from fastapi import APIRouter, Depends

from shared.game_specs import GAMES
from ..depends.http import get_http_client
from ..services.error import error


router = APIRouter(prefix="/games", tags=["games"])

@router.get("/{game}/start")
async def start_game(game: str, http=Depends(get_http_client)) -> dict:
    '''
    Returns the init state for the requested game.
    '''
    engine = await select_engine(game, http)
    return engine.init_state()


@router.post("/{game}/move")
async def play_move(game: str, payload: dict,
                    http=Depends(get_http_client)) -> dict:
    '''
    Returns the updated state for the requested game.
    '''
    engine = await select_engine(game, http)
    return engine.update_state(payload["state"], payload["action"])


async def select_engine(game: str, http):
    '''
    Returns the appropriate game engine.
    '''
    # use .get() to avoid KeyError
    game_cfg = GAMES.get(game)   # cfg: config
    if not game_cfg:
        raise error(404, f"Unknown game: {game}")

    engine_cls = game_cfg['engine']   # cls: class
    engine = engine_cls()

    # not all engines implement setup()
    # getattr more secure than hastattr() b/c
    # engine.setup can be dynamically overwritten
    setup = getattr(engine, 'setup', None)   # equiv to engine.setup
    if callable(setup):
        await setup(http)

    return engine


