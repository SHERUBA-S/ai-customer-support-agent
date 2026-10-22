import time
from typing import Dict, List
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.core.config import settings

security_scheme = HTTPBearer(auto_error=False)

# In-memory IP rate limiter: {ip: [timestamps]}
RATE_LIMIT_STORE: Dict[str, List[float]] = {}


def check_rate_limit(request: Request):
    """
    Sliding window rate limiter based on client IP.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    window = 60.0  # 1 minute
    max_requests = settings.RATE_LIMIT_PER_MINUTE

    timestamps = RATE_LIMIT_STORE.get(client_ip, [])
    # Filter out requests older than the window
    timestamps = [t for t in timestamps if now - t < window]

    if len(timestamps) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before sending more requests."
        )

    timestamps.append(now)
    RATE_LIMIT_STORE[client_ip] = timestamps


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> str:
    """
    Dependency to require and validate admin JWT bearer token.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in as an administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier.",
        )

    return username
