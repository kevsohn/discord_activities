from datetime import datetime, timezone, timedelta

from ..config import GAME_RESET_HOUR


def get_current_epoch() -> str:
    """
    Returns the current epoch as YYYY-MM-DD (UTC).
    """
    now = datetime.now(timezone.utc)
    return now.date().isoformat()  # .iso for json-serializable


def seconds_til_next_reset() -> int:
    '''
    Returns the next reset time in seconds for redis TTL.
    '''
    now = datetime.now(timezone.utc)

    next_reset = now.replace(
        hour=GAME_RESET_HOUR,
        minute=0,
        second=0,
        microsecond=0,
    )

    if now >= next_reset:
        next_reset += timedelta(days=1)

    return int((next_reset-now).total_seconds())

