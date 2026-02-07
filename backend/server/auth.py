"""
Authentication module for GPT Researcher.
Provides JWT-based authentication with preset accounts (no registration).
"""

import os
import time
import hashlib
import hmac
import json
import logging
from typing import Optional
from fastapi import HTTPException, Request, WebSocket, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# JWT-like token implementation using HMAC-SHA256 (no external dependency needed)
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "gpt-researcher-default-secret-change-me")
TOKEN_EXPIRE_HOURS = int(os.getenv("AUTH_TOKEN_EXPIRE_HOURS", "24"))

# Whether auth is enabled (disabled by default for local dev)
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"


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


def authenticate_user(username: str, password: str) -> Optional[str]:
    """Check credentials against preset users. Returns username if valid."""
    users = _get_preset_users()
    if username in users and users[username] == password:
        return username
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
