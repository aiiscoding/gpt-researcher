"""
Authentication module for GPT Researcher.
Provides JWT-based authentication with preset accounts (no registration).
Includes brute-force protection with IP-based rate limiting.
"""

import os
import time
import hashlib
import hmac
import json
import logging
from collections import defaultdict
from typing import Optional
from fastapi import HTTPException, Request, WebSocket, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# JWT-like token implementation using HMAC-SHA256 (no external dependency needed)
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "gpt-researcher-default-secret-change-me")
TOKEN_EXPIRE_HOURS = int(os.getenv("AUTH_TOKEN_EXPIRE_HOURS", "24"))

# Whether auth is enabled (disabled by default for local dev)
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"

# Brute-force protection: max failed attempts per IP before lockout
_MAX_FAILED_ATTEMPTS = int(os.getenv("AUTH_MAX_FAILED_ATTEMPTS", "5"))
_LOCKOUT_SECONDS = int(os.getenv("AUTH_LOCKOUT_SECONDS", "900"))  # 15 minutes
_failed_attempts: dict[str, list[float]] = defaultdict(list)


class LoginRequest(BaseModel):
    username: str
    password: str


def _get_preset_users() -> dict:
    """Load preset users from environment variable.

    Format: AUTH_USERS="user1:password1,user2:password2"
    Default: admin:admin123
    """
    users_str = os.getenv("AUTH_USERS", "admin:admin123")
    users = {}
    for entry in users_str.split(","):
        entry = entry.strip()
        if ":" in entry:
            username, password = entry.split(":", 1)
            users[username.strip()] = password.strip()
    return users


def _b64_encode(data: bytes) -> str:
    """URL-safe base64 encode without padding."""
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64_decode(s: str) -> bytes:
    """URL-safe base64 decode with padding restoration."""
    import base64
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def create_token(username: str) -> str:
    """Create a signed token containing username and expiration."""
    expire_at = int(time.time()) + TOKEN_EXPIRE_HOURS * 3600
    payload = json.dumps({"sub": username, "exp": expire_at}).encode("utf-8")
    payload_b64 = _b64_encode(payload)
    signature = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_token(token: str) -> Optional[str]:
    """Verify token signature and expiration. Returns username or None."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload = json.loads(_b64_decode(payload_b64))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload.get("sub")
    except Exception:
        return None


def _get_client_ip(request: Request) -> str:
    """Get client IP, respecting X-Forwarded-For behind reverse proxy."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _check_rate_limit(ip: str) -> None:
    """Raise 429 if the IP has too many recent failed login attempts."""
    now = time.time()
    cutoff = now - _LOCKOUT_SECONDS
    # Clean old entries
    _failed_attempts[ip] = [t for t in _failed_attempts[ip] if t > cutoff]
    if len(_failed_attempts[ip]) >= _MAX_FAILED_ATTEMPTS:
        remaining = int(_LOCKOUT_SECONDS - (now - _failed_attempts[ip][0]))
        logger.warning(f"Login rate limit hit for IP {ip}, locked for {remaining}s")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Try again in {remaining} seconds.",
        )


def _record_failed_attempt(ip: str) -> None:
    """Record a failed login attempt for rate limiting."""
    _failed_attempts[ip].append(time.time())


def _clear_failed_attempts(ip: str) -> None:
    """Clear failed attempts on successful login."""
    _failed_attempts.pop(ip, None)


def authenticate_user(username: str, password: str, request: Optional[Request] = None) -> Optional[str]:
    """Check credentials against preset users. Returns username if valid.
    Enforces rate limiting when request is provided.
    """
    if request:
        ip = _get_client_ip(request)
        _check_rate_limit(ip)

    users = _get_preset_users()
    if username in users and users[username] == password:
        if request:
            _clear_failed_attempts(_get_client_ip(request))
        return username

    if request:
        ip = _get_client_ip(request)
        _record_failed_attempt(ip)
        attempts_left = _MAX_FAILED_ATTEMPTS - len(_failed_attempts[ip])
        logger.warning(f"Failed login for '{username}' from {ip} ({attempts_left} attempts left)")

    return None


def get_token_from_request(request: Request) -> Optional[str]:
    """Extract bearer token from Authorization header or cookie."""
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return request.cookies.get("auth_token")


def get_token_from_websocket(websocket: WebSocket) -> Optional[str]:
    """Extract token from WebSocket query params or cookies."""
    token = websocket.query_params.get("token")
    if token:
        return token
    return websocket.cookies.get("auth_token")


async def require_auth(request: Request) -> str:
    """Dependency: require valid authentication. Returns username."""
    if not AUTH_ENABLED:
        return "anonymous"
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


async def require_auth_ws(websocket: WebSocket) -> Optional[str]:
    """Check WebSocket authentication. Returns username or None."""
    if not AUTH_ENABLED:
        return "anonymous"
    token = get_token_from_websocket(websocket)
    if not token:
        return None
    return verify_token(token)
