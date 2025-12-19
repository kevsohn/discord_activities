'''
Game logic interface for the frontend
'''
from fastapi import APIRouter, Depends

from ..depends.session import get_session_id, get_session_manager
from ..depends.engine_reg import get_game_engine
from ..depends.game_state import get_state_cache


router = APIRouter(prefix="/games", tags=["games"])

# session_id gated
@router.get("/{game_id}/start")
async def start_game(game_id: str,
                     session_id = Depends(get_session_id),
                     session = Depends(get_session_manager),
                     engine = Depends(get_game_engine),
                     state_cache = Depends(get_state_cache)) -> dict:
    '''
    Returns the init state for the requested game.
    '''
    # key must match fetch_user_info() in api/auth.py
    user_id = session.get(session_id)['id']  # want KeyError

    reset = await engine.ensure_daily_reset()
    if reset:
        state = engine.get_init_state()
        await state_cache.store(user_id, game_id, state)
        return state

    return await state_cache.get(user_id, game_id)


# session_id gated
@router.post("/{game_id}/move")
async def play_move(game_id: str,
                    payload: dict,
                    session_id = Depends(get_session_id),
                    session = Depends(get_session_manager),
                    engine = Depends(get_game_engine),
                    state_cache = Depends(get_state_cache)) -> dict:
    '''
    Returns the updated state for the requested game.
    '''
    user_id = session.get(session_id)['id']
    state = engine.update_state(payload["state"], payload["action"])
    await state_cache.store(user_id, game_id, state)

    return state


