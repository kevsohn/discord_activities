'''
Game logic interface for the frontend
'''
from fastapi import APIRouter, HTTPException
from config import GAMES

# just like Flask Blueprints
router = APIRouter(prefix="/games", tags=["games"])

@router.get("/{game}/start")
def start_game(game: str) -> dict:
    '''
    Returns the init state for the requested game.
    '''
    engine = get_engine(game)
    return engine.init_state()


@router.post("/{game}/move")
def play_move(game: str, payload: dict) -> dict:
    '''
    Returns the updated state for the requested game.
    '''
    engine = get_engine(game)
    return engine.update_state(payload["state"], payload["action"])


def get_engine(game: str):
    '''
    Helper fnc that returns the appropriately init'd game engine.
    '''
    # use .get() to avoid KeyError
    game_cfg = GAMES.get(game)  # cfg stands for config
    if not game_cfg:
        raise HTTPException(404, f"Unknown game: {game}")

    engine_cls = game_cfg['engine']  # cls stands for class
    data_fn = game_cfg['provider']

    # if this game requires data from an API
    if data_fn:
        data = data_fn()
        return engine_cls(**data)  # constructors can have diff args

    return engine_cls()

