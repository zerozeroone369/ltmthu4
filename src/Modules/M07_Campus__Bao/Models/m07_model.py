"""PostgreSQL Model (psycopg) cho M7: Campus (Tin tức, Học bổng, Sự kiện) (Bảo)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["TinTruong"]


def get_module_health() -> dict:
    return {
        "module": "M7",
        "owner": "Bảo",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
