"""PostgreSQL Model (psycopg) cho M10: Quản trị Hệ thống & Kiểm duyệt (Admin) (Nguyễn Ngô Tú Anh)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["BaoCaoViPham", "NguoiDung"]


def get_module_health() -> dict:
    return {
        "module": "M10",
        "owner": "Nguyễn Ngô Tú Anh",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
