"""PostgreSQL Model (psycopg) cho M6: Nhóm học Tập (Study Groups) (Bảo)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["NhomHoc", "ThanhVienNhom"]


def get_module_health() -> dict:
    return {
        "module": "M6",
        "owner": "Bảo",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
