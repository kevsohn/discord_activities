'''
Discord provides its own session id.
'''
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from secrets import token_urlsafe

from ..depends.sessions import get_session_manager, get_session_id
from ..services.reset import seconds_til_next_reset
from ..services.error import error


router = APIRouter(prefix="/api/session")

# pydantic model: parses JSON from request body and handles errors
class CreateRequest(BaseModel):
    user_id: str


@router.post('/create')
async def create_session(body: CreateRequest,
                         sessions = Depends(get_session_manager)):
    '''
    Frontend sends session id and discord id.
    Backend:
     - creates session in Redis
     - sets and returns HTTP-only session cookie
    '''
    session_id = token_urlsafe(32)
    await sessions.create(session_id, body.user_id)

    r = JSONResponse({})
    r.set_cookie(
        key='session_id',
        value=session_id,
        httponly=True,
        secure=True,      # HTTPS
        samesite='none',  # req for Activities iframe
        max_age=seconds_til_next_reset(),  # != sessions.ttl
        path='/'  # controls which urls the browser sends cookies to
    )
    return r


# session id gated
@router.post('/heartbeat')
async def heartbeat(session_id: str = Depends(get_session_id),
                    sessions = Depends(get_session_manager)):
    '''
    Frontend sends heartbeat every 20 secs;
    Backend extends session ttl every beat.
    '''
    ok = await sessions.heartbeat(session_id)
    if not ok:
        raise error(404, 'Session expired')
    return JSONResponse({'ok': True})


