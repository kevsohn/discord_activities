from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from secrets import token_urlsafe

from ..config import SESSION_TTL, DISCORD_API_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from ..depends.http import get_http_client
from ..depends.sessions import get_session_manager
from ..services.error import error


router = APIRouter(prefix="/api/auth")

@router.post('/token')
async def exchange_code(code: str,
                        http=Depends(get_http_client),
                        sessions=Depends(get_session_manager)) -> str:
    '''
    Frontend sends Discord OAuth2 code.
    Backend:
     - exchanges code for access token
     - fetches Discord user
     - stores session in Redis
     - sets HTTP-only session cookie
     - returns access token
    '''
    access_token = await fetch_access_token(code, http)
    user_info = await fetch_user_info(access_token, http)

    session_id = token_urlsafe(32)  # 256-bit entropy
    await sessions.create(session_id, user_info)

    r = JSONResponse({'access_token': access_token})
    r.set_cookie(
        key='session_id',
        value=session_id,
        httponly=True,
        secure=True,          # HTTPS
        samesite='none',      # req for Activities iframe
        max_age=sessions.ttl,
    )
    return r


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


async def fetch_user_info(access_token: str, http) -> dict:
    """
    Returns:
    {
        id: int
        username: str
        discriminator: int (differentiates users w/ same uname)
        avatar:
    }
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    r = await http.get(
            f'{DISCORD_API_URL}/users/@me',
            headers = headers,
    )
    if r.status_code != 200:
        raise error(r.status_code, 'Invalid Discord token')

    return r.json()


