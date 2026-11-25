"""PostgreSQL database connection helper using psycopg3."""
import os
from contextlib import contextmanager

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")


def get_database_url() -> str:
    """Resolve DATABASE_URL dynamically so .env or runtime env updates take effect."""
    return os.getenv("DATABASE_URL", "") or DATABASE_URL


@contextmanager
def get_conn():
    url = get_database_url()
    if not url:
        raise RuntimeError("Chưa cấu hình biến môi trường DATABASE_URL cho PostgreSQL.")
    conn = psycopg.connect(url, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def check_db_health() -> dict:
    url = get_database_url()
    if not url:
        return {"connected": False, "detail": "Chưa gắn DATABASE_URL"}
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*)::int AS total_tables FROM information_schema.tables WHERE table_schema = %s",
                ("public",),
            )
            row = cur.fetchone()
            return {"connected": True, "tables": row["total_tables"]}
    except (psycopg.Error, OSError, RuntimeError) as exc:
        return {"connected": False, "detail": str(exc)}
