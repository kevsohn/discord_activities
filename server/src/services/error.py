from fastapi import HTTPException

from ..config import REQUEST_TIMEOUT

def error(status_code: int, msg: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=msg)
