"""PostgreSQL Model (psycopg) cho M8: Khung Tkinter Chung, Bảng tin & Riêng tư (Thái)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["NguoiDung", "KetBan"]


def get_module_health() -> dict:
    return {
        "module": "M8",
        "owner": "Thái",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
