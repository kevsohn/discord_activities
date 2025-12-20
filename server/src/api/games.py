'''
Game logic interface for the frontend
'''
from fastapi import APIRouter, Depends

from ..depends.sessions import get_session_id, get_session_manager
from ..depends.engine_reg import get_game_engine
from ..depends.game_states import get_state_cache
from ..depends.db import get_db
from ..services.persist import save_score


router = APIRouter(prefix="/games", tags=["games"])

# session_id gated
@router.get("/{game_id}/start")
async def start(game_id: str,
                session_id=Depends(get_session_id),
                sessions=Depends(get_session_manager),
                engine=Depends(get_game_engine),
                state_cache=Depends(get_state_cache)) -> dict:
    '''
    Returns the init state for the requested game.
    '''
    # key must match fetch_user_info() in api/auth.py
    user_id = sessions.get(session_id)['id']  # want KeyError

    reset = await engine.ensure_daily_reset()
    if reset:
        state = engine.get_init_state()
        await state_cache.store(user_id, game_id, state)
        return state
    # get from db?
    return await state_cache.get(user_id, game_id)


# session_id gated
@router.post("/{game_id}/update")
async def update(game_id: str,
                 payload: dict,
                 session_id=Depends(get_session_id),
                 sessions=Depends(get_session_manager),
                 engine=Depends(get_game_engine),
                 state_cache=Depends(get_state_cache)) -> dict:
    '''
    Returns the updated state for the requested game.
    '''
    user_id = sessions.get(session_id)['id']
    state = engine.update_state(payload["state"], payload["action"])
    await state_cache.store(user_id, game_id, state)
    return state


# session_id gated
@router.post("/{game_id}/gameover")
async def gameover(game_id: str,
                   payload: dict,
                   session_id=Depends(get_session_id),
                   sessions=Depends(get_session_manager),
                   db=Depends(get_db)):
    user_id = sessions.get(session_id)['id']
    score = payload['score']
    await save_score(db, game_id, user_id, score)


