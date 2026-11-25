"""JWT & NguoiDung verification helpers (Tú Anh - M01)."""
from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException

from src.Shared.config.db import get_conn, get_database_url

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-env")
JWT_ALG = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

_REVOKED_LOCK = Lock()
_REVOKED_TOKENS: dict[str, float] = {}


def get_jwt_secret() -> str:
    """Resolve JWT secret dynamically from environment or module fallback."""
    return os.getenv("JWT_SECRET", "") or JWT_SECRET


def _prune_revoked_locked(now_ts: float) -> None:
    expired = [jti for jti, exp_ts in _REVOKED_TOKENS.items() if exp_ts <= now_ts]
    for jti in expired:
        _REVOKED_TOKENS.pop(jti, None)


def revoke_token(payload: dict) -> None:
    """Mark a decoded token's JTI as revoked until its expiration timestamp."""
    jti = payload.get("jti")
    if not jti:
        return
    now_ts = datetime.now(UTC).timestamp()
    exp_val = payload.get("exp")
    exp_ts = float(exp_val) if exp_val is not None else now_ts + JWT_EXPIRE_MINUTES * 60
    with _REVOKED_LOCK:
        _prune_revoked_locked(now_ts)
        _REVOKED_TOKENS[str(jti)] = exp_ts


def is_token_revoked(payload: dict) -> bool:
    """Check whether the given token payload has been revoked via logout."""
    jti = payload.get("jti")
    if not jti:
        return False
    now_ts = datetime.now(UTC).timestamp()
    with _REVOKED_LOCK:
        _prune_revoked_locked(now_ts)
        return str(jti) in _REVOKED_TOKENS


def clear_revoked_tokens() -> None:
    """Clear in-memory revoked token cache (used in tests)."""
    with _REVOKED_LOCK:
        _REVOKED_TOKENS.clear()


def create_access_token(
    user_id: int,
    email: str,
    role: str,
    expires_minutes: int | None = None,
) -> tuple[str, int]:
    """Issue a signed HS256 JWT access token and return (token, expires_in_seconds)."""
    ttl_minutes = expires_minutes if expires_minutes is not None else JWT_EXPIRE_MINUTES
    now = datetime.now(UTC)
    exp = now + timedelta(minutes=ttl_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "jti": uuid.uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALG)
    return token, ttl_minutes * 60


def fetch_active_user_auth_state(user_id: int) -> dict | None:
    """Load current status and role from NguoiDung to enforce real-time lock/role checks."""
    if not get_database_url():
        return {"_db_disabled": True}
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaNguoiDung", "TrangThai", "VaiTro", "Email", "HoTen", "MaLop"
            FROM "NguoiDung"
            WHERE "MaNguoiDung" = %s
            """,
            (user_id,),
        )
        return cur.fetchone()


def decode_and_validate_token(token: str) -> dict:
    """Decode JWT, reject revoked tokens, and validate user status against NguoiDung."""
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALG])
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Token không hợp lệ hoặc đã hết hạn: {exc}") from exc

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token thiếu thông tin người dùng.")
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Định dạng mã người dùng trong token không hợp lệ.") from exc

    if is_token_revoked(payload):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập đã đăng xuất, vui lòng đăng nhập lại.")

    payload["user_id"] = user_id
    state = fetch_active_user_auth_state(user_id)
    if state and state.get("_db_disabled"):
        return payload
    if not state or state.get("TrangThai") != "HoatDong":
        raise HTTPException(status_code=401, detail="Tài khoản không hoạt động hoặc đã bị khóa.")

    payload["role"] = state["VaiTro"]
    payload["email"] = state["Email"]
    payload["full_name"] = state["HoTen"]
    payload["class_id"] = state.get("MaLop")
    return payload


def verify_token(authorization: str = Header(default="")) -> dict:
    """Extract and validate Bearer JWT from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu Bearer Token xác thực.")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Bearer Token rỗng.")
    return decode_and_validate_token(token)


def require_admin(user: Annotated[dict, Depends(verify_token)]) -> dict:
    """Enforce QuanTriVien role on administrative routes."""
    if user.get("role") != "QuanTriVien":
        raise HTTPException(status_code=403, detail="Chỉ Quản trị viên (QuanTriVien) được phép thực hiện.")
    return user
