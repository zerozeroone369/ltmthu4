"""JWT & NguoiDung verification helpers (Tú Anh - M01)."""
import os
from fastapi import Depends, HTTPException, Header
import jwt
from src.Shared.config.db import DATABASE_URL, get_conn

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-env")
JWT_ALG = "HS256"


def decode_and_validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Token không hợp lệ hoặc đã hết hạn: {exc}")

    if DATABASE_URL and payload.get("sub"):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT "TrangThai" AS user_status, "VaiTro" AS role_name
                FROM "NguoiDung"
                WHERE "MaNguoiDung" = %s
                """,
                (int(payload["sub"]),),
            )
            row = cur.fetchone()
            if not row or row["user_status"] != "HoatDong":
                raise HTTPException(status_code=401, detail="Tài khoản không hoạt động hoặc đã bị khóa.")
            payload["role"] = row["role_name"]
    return payload


def verify_token(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu Bearer Token xác thực.")
    return decode_and_validate_token(authorization[7:].strip())


def require_admin(user: dict = Depends(verify_token)) -> dict:
    if user.get("role") != "QuanTriVien":
        raise HTTPException(status_code=403, detail="Chỉ Quản trị viên (QuanTriVien) được phép thực hiện.")
    return user
