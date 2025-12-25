'''
Game logic interface for the frontend
'''
from fastapi import APIRouter, Depends

from ..depends.redis import get_redis
from ..depends.sessions import get_session_id, get_session_manager
from ..depends.engine_reg import get_game_engine
from ..depends.game_states import get_state_store
from ..depends.streak import mark_played
from ..services.leaderboard import rank_player
from ..services.reset import get_current_epoch, seconds_til_next_reset

router = APIRouter(prefix="/games", tags=["games"])


# session_id gated
# mark_played checks if streak should be incremented
@router.get("/{game_id}/start")
async def start(game_id: str,
                session_id=Depends(get_session_id),
                sessions=Depends(get_session_manager),
                engine=Depends(get_game_engine),
                states=Depends(get_state_store),
                _=Depends(mark_played)) -> dict:
    '''
    Returns the init state for the requested game.
    '''
    session = await sessions.get(session_id)

    # key must match fetch_user_info() in api/auth.py
    user_id = session['id']  # want KeyError
    if user_id is None:
        raise error(401, 'Session expired')

    epoch = get_current_epoch()
    state = await states.get(game_id, user_id, epoch)

    is_reset = await engine.ensure_reset(epoch)
    if state is None or is_reset:
        # order matters in case user plays close to reset
        # want state to timeout first
        ttl = seconds_til_next_reset()
        state = engine.get_init_state()
        await states.store(game_id, user_id, epoch, state, ttl)

    return state


# session_id gated
@router.post("/{game_id}/update")
async def update(game_id: str,
                 payload: dict,
                 session_id=Depends(get_session_id),
                 sessions=Depends(get_session_manager),
                 engine=Depends(get_game_engine),
                 states=Depends(get_state_store),
                 redis=Depends(get_redis)) -> dict:
    '''
    Returns the updated state for the requested game.
    '''
    session = await sessions.get(session_id)

    # key must match fetch_user_info() in api/auth.py
    user_id = session['id']  # want KeyError
    if user_id is None:
        raise error(401, 'Session expired')

    # get ttl here so its consistent with current epoch.
    # otherwise, might store w/ next epoch's ttl.
    epoch = get_current_epoch()
    ttl = seconds_til_next_reset()

    # in case game resets during play
    is_reset = await engine.ensure_reset(epoch)
    if is_reset:
        raise error(409, 'Game reset, restart required')

    state = engine.update_state(payload["state"], payload["action"])
    await states.store(game_id, user_id, epoch, state, ttl)

    # live leaderboard update
    await rank_player(game_id, user_id, epoch, state['score'], redis)

    return state


# session_id gated
@router.post("/{game_id}/gameover")
async def gameover(session_id=Depends(get_session_id)):
    pass

