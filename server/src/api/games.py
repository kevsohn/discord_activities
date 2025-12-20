'''
Game logic interface for the frontend
'''
from fastapi import APIRouter, Depends

from ..depends.sessions import get_session_id, get_session_manager
from ..depends.engine_reg import get_game_engine
from ..depends.game_states import get_state_store
from ..depends.db_session import get_db_session


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
    state = await states.get(user_id, game_id)

    reset = await engine.ensure_daily_reset()
    if state is None or reset:
        state = engine.get_init_state()
        await states.store(user_id, game_id, state)

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
    state = engine.update_state(payload["state"], payload["action"])
    await states.store(user_id, game_id, state)
    return state


# session_id gated
@router.post("/{game_id}/gameover")
async def gameover(game_id: str,
                   payload: dict,
                   session_id=Depends(get_session_id),
                   sessions=Depends(get_session_manager),
                   db=Depends(get_db_session)):
    # do nothing?
    pass


