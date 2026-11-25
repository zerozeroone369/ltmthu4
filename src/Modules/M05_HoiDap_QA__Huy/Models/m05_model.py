"""PostgreSQL Model (psycopg) cho M5: Hỏi đáp Học thuật (Q&A & Upvote) (Huy)."""
from src.Shared.config.db import DATABASE_URL

TABLES = ["CauHoi", "CauTraLoi", "BinhChonCauTraLoi"]


def get_module_health() -> dict:
    return {
        "module": "M5",
        "owner": "Huy",
        "tables": TABLES,
        "db_configured": bool(DATABASE_URL),
    }
