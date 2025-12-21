from datetime import datetime, timedelta

from ..config import GAME_RESET_HOUR


def get_current_epoch() -> str:
    """
    Returns the current epoch as YYYY_MM_DD@HH
    """
    now = datetime.utcnow()
    return f'{now.date().isoformat()}@{GAME_RESET_HOUR:02d}'


def seconds_til_next_reset() -> int:
    '''
    Returns the next reset time in seconds for redis TTL.
    '''
    now = datetime.utcnow()

    next_reset = now.replace(
        hour=RESET_HOUR,
        minute=0,
        second=0,
        microsecond=0,
    )

    if now >= next_reset:
        next_reset += timedelta(days=1)

    return int((next_reset-now).total_seconds())

