"""PostgreSQL Model (psycopg) cho M2: Cây Cộng đồng 5 Cấp (Trường → Lớp) (Duy)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["CongDong"]


def get_module_health() -> dict:
    return {
        "module": "M2",
        "owner": "Duy",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
