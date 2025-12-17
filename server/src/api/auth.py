from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
import requests
from config import DISCORD_API_URL, CLIENT_ID, CLIENT_SECRET
from services import sessions

router = APIRouter(prefix="/api")

@router.post('/token')
def exchange_code(code: str) -> str:
    '''
    Frontend sends discord code, backend exchanges it for an access token,
    creates a session id and returns both.
    '''
    # access_t is used to auth with Discord SDK in the frontend
    # still need a session id for internal auth
    access_t = fetch_access_token(code)
    user = fetch_discord_user(access_t)
    session_id = sessions.create_session(user['id'])

    r = JSONResponse({'access_token': access_t})
    r.set_cookie(
        'session_id',
        session_id,
        httponly=True,
        secure=True,
        samesite='none'
    )
    return r


def fetch_access_token(code: str) -> dict:
    """
    Exchanges discord code for discord access token
    """
    # redirect_uri needs to match exactly with the dev page one
    data = {'grant_type': 'authorization_code',
            'code': code,
            #'redirect_uri': app.config['REDIR_URI']
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(
            f'{DISCORD_API_URL}/oauth2/token',
            data = data,
            headers = headers,
            auth = (CLIENT_ID, CLIENT_SECRET)
    )
    r.raise_for_status()

    data = r.json()  # access_t, token_type, expires_in, refresh_t, scope
    return data['access_token']


def fetch_discord_user(access_token: str) -> dict:
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

    r = requests.get(f"{DISCORD_API_URL}/users/@me",
                     headers=headers
    )
    r.raise_for_status()
    return r.json()


