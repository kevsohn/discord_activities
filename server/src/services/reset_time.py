from datetime import datetime, timedelta

# make sure everything that uses this is tz-agnostic
def next_reset_time() -> datetime:
    '''Returns the next reset time.'''
    now = datetime.utcnow()
    tmr = now.date() + timedelta(days=1)
    # min.time == 00:00:00 -> tmr midnight
    return datetime.combine(tmr, datetime.min.time())
