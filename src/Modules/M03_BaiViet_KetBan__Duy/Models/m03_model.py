"""PostgreSQL Model (psycopg) cho M3: Bài viết, Tương tác & Kết bạn (Duy)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["BaiViet", "BinhLuan", "TuongTac", "KetBan"]


def get_module_health() -> dict:
    return {
        "module": "M3",
        "owner": "Duy",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
