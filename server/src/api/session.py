'''
Discord provides its own session id.
'''
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from secrets import token_urlsafe

from ..depends.sessions import get_session_manager, get_session_id

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
     - sets HTTP-only session cookie
     - returns cookie
    '''
    session_id = token_urlsafe(32)
    await sessions.create(session_id, body.user_id)

    r = JSONResponse({})
    r.set_cookie(
        key='session_id',
        value=session_id,
        httponly=True,
        secure=True,          # HTTPS
        samesite='none',      # req for Activities iframe
        max_age=sessions.ttl,
    )
    return r


# session id gated
@router.post('/delete')
async def create_session(session_id: str = Depends(get_session_id),
                         sessions = Depends(get_session_manager)):
    '''
    Deletes stored session id on user disconnect.
    '''
    await sessions.delete(session_id)

    r = JSONResponse({})
    r.delete_cookie("session_id")
    return r

