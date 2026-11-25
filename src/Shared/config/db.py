"""PostgreSQL database connection helper using psycopg3."""
import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "")


@contextmanager
def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("Chưa cấu hình biến môi trường DATABASE_URL cho PostgreSQL.")
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def check_db_health() -> dict:
    if not DATABASE_URL:
        return {"connected": False, "detail": "Chưa gắn DATABASE_URL"}
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*)::int AS total_tables FROM information_schema.tables WHERE table_schema = %s",
                ("public",),
            )
            row = cur.fetchone()
            return {"connected": True, "tables": row["total_tables"]}
    except Exception as exc:
        return {"connected": False, "detail": str(exc)}
