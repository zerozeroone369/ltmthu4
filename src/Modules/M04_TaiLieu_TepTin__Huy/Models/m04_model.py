"""PostgreSQL Model (psycopg) cho M4: Tài liệu Học tập & Truyền tệp (Huy)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["MonHoc", "TaiLieu", "DanhGiaTaiLieu"]


def get_module_health() -> dict:
    return {
        "module": "M4",
        "owner": "Huy",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
