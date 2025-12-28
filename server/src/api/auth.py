from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..config import DISCORD_API_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from ..depends.http import get_http_client
from ..depends.sessions import get_session_manager
from ..services.error import error

router = APIRouter(prefix="/api/auth")


# pydantic model: parses JSON from request body and handles errors
class TokenRequest(BaseModel):
    code: str


@router.post('/token')
async def exchange_code(body: TokenRequest,
                        http=Depends(get_http_client),
                        sessions=Depends(get_session_manager)) -> str:
    '''
    Frontend sends Discord OAuth2 code.
    Backend:
     - exchanges code for access token
     - returns access token
    '''
    code = body.code
    access_token = await fetch_access_token(code, http)
    return JSONResponse({'access_token': access_token})


async def fetch_access_token(code: str, http) -> dict:
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI  # needs to match in disc dev page
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = await http.post(
            f'{DISCORD_API_URL}/oauth2/token',
            data = data,
            headers = headers,
    )
    if r.status_code != 200:
        raise error(r.status_code, 'Failed to exchange code')

    data = r.json()  # access_t, token_type, expires_in, refresh_t, scope
    return data['access_token']

