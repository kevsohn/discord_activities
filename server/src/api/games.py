'''
Game logic interface for the frontend
'''
from fastapi import APIRouter, Depends

from ..depends.sessions import get_session_id, get_session_manager
from ..depends.engine_reg import get_game_engine
from ..depends.game_states import get_state_store
from ..services.reset import get_current_epoch, seconds_til_next_reset


router = APIRouter(prefix="/games", tags=["games"])

# session_id gated
@router.get("/{game_id}/start")
async def start(game_id: str,
                session_id=Depends(get_session_id),
                sessions=Depends(get_session_manager),
                engine=Depends(get_game_engine),
                states=Depends(get_state_store)) -> dict:
    '''
    Returns the init state for the requested game.
    '''
    # key must match fetch_user_info() in api/auth.py
    user_id = sessions.get(session_id)['id']  # want KeyError
    if user_id is None:
        raise error(401, 'Session expired')

    epoch = get_current_epoch()
    state = await states.get(game_id, user_id, epoch)

    is_reset = await engine.ensure_reset(epoch)
    if state is None or is_reset:
        state = engine.get_init_state()
        ttl = seconds_til_next_reset()
        await states.store(game_id, user_id, epoch, state, ttl)

    return state


# session_id gated
@router.post("/{game_id}/update")
async def update(game_id: str,
                 payload: dict,
                 session_id=Depends(get_session_id),
                 sessions=Depends(get_session_manager),
                 engine=Depends(get_game_engine),
                 states=Depends(get_state_store)) -> dict:
    '''
    Returns the updated state for the requested game.
    '''
    user_id = sessions.get(session_id)['id']
    if user_id is None:
        raise error(401, 'Session expired')

    epoch = get_current_epoch()
    state = engine.update_state(payload["state"], payload["action"])
    ttl = seconds_til_next_reset()
    await states.store(game_id, user_id, epoch, state, ttl)

    return state


# session_id gated
@router.post("/{game_id}/gameover")
async def gameover(session_id=Depends(get_session_id)):
    pass


