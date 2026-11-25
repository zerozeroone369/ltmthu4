"""PostgreSQL Model (psycopg) cho M1: Tài khoản, Hồ sơ & Quên mật khẩu (OTP) (Nguyễn Ngô Tú Anh)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["NguoiDung"]


def get_module_health() -> dict:
    return {
        "module": "M1",
        "owner": "Nguyễn Ngô Tú Anh",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
