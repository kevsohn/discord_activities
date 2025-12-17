from redis import redis_client
from secrets import token_urlsafe
from config import SESSION_TTL

def create_session(user_id: str) -> str:
    '''
    Stores user id in a Redis db and returns session id
    '''
    session_id = token_urlsafe(32)
    redis_client.setex(f'session:{session_id}', SESSION_TTL, user_id)
    return session_id


def delete_session(session_id: str):
    redis_client.delete(f'session:{session_id}')


def get_user_id(session_id: str) -> str:
    if not session_id:
        return None
    return redis_client.get(f'session:{session_id}')
