"""PostgreSQL Model (psycopg) cho M9: Nhắn tin Realtime & Thông báo (Thái)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["TinNhan", "ThongBao"]


def get_module_health() -> dict:
    return {
        "module": "M9",
        "owner": "Thái",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
