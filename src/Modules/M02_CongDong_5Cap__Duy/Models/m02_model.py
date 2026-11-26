"""PostgreSQL Model (psycopg) cho M2: Cây Cộng đồng 5 Cấp (Trường → Lớp) (Duy)."""
from __future__ import annotations

import psycopg

from src.Shared.config.db import get_conn, get_database_url

TABLES = ["CongDong"]

_COMMUNITY_COLS = """
    "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong",
    "CapDo", "NamBatDau", "TrangThai"
"""


def get_module_health() -> dict:
    return {
        "module": "M2",
        "owner": "Duy",
        "tables": TABLES,
        "db_configured": bool(get_database_url()),
    }


def get_community_by_id(community_id: int) -> dict | None:
    """Fetch one CongDong node by primary key."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f'SELECT {_COMMUNITY_COLS} FROM "CongDong" WHERE "MaCongDong" = %s',
            (community_id,),
        )
        return cur.fetchone()


def get_community_children(parent_id: int | None = None, include_inactive: bool = False) -> list[dict]:
    """Fetch direct child CongDong rows (or root Truong nodes when parent_id is None)."""
    clauses: list[str] = ['"MaCongDongCha" IS NULL' if parent_id is None else '"MaCongDongCha" = %s']
    params: list[object] = [] if parent_id is None else [parent_id]
    if not include_inactive:
        clauses.append('"TrangThai" = %s')
        params.append("DangHoatDong")

    where_sql = " AND ".join(clauses)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f'SELECT {_COMMUNITY_COLS} FROM "CongDong" WHERE {where_sql} ORDER BY "TenCongDong" ASC',
            tuple(params),
        )
        return list(cur.fetchall())


def list_communities(
    *,
    cap_do: str | None = None,
    trang_thai: str | None = None,
    parent_id: int | None = None,
    search: str = "",
    include_inactive: bool = True,
) -> list[dict]:
    """Query CongDong nodes with optional level, parent, status, and keyword filters."""
    clauses: list[str] = []
    params: list[object] = []

    if cap_do:
        clauses.append('"CapDo" = %s')
        params.append(cap_do)
    if trang_thai:
        clauses.append('"TrangThai" = %s')
        params.append(trang_thai)
    elif not include_inactive:
        clauses.append('"TrangThai" = %s')
        params.append("DangHoatDong")
    if parent_id is not None:
        clauses.append('"MaCongDongCha" = %s')
        params.append(parent_id)
    if search.strip():
        pattern = f"%{search.strip()}%"
        clauses.append('("TenCongDong" ILIKE %s OR COALESCE("KyHieu", \'\') ILIKE %s)')
        params.extend([pattern, pattern])

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT {_COMMUNITY_COLS}
            FROM "CongDong"
            {where_sql}
            ORDER BY COALESCE("MaCongDongCha", 0) ASC, "TenCongDong" ASC, "MaCongDong" ASC
            """,
            tuple(params),
        )
        return list(cur.fetchall())


def get_community_chain(community_id: int) -> list[dict]:
    """Resolve ancestor chain from root Truong down to the requested CongDong node."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            WITH RECURSIVE chain AS (
                SELECT "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong",
                       "CapDo", "NamBatDau", "TrangThai", 0 AS depth
                FROM "CongDong"
                WHERE "MaCongDong" = %s
                UNION ALL
                SELECT p."MaCongDong", p."MaCongDongCha", p."KyHieu", p."TenCongDong",
                       p."CapDo", p."NamBatDau", p."TrangThai", c.depth + 1
                FROM "CongDong" p
                JOIN chain c ON p."MaCongDong" = c."MaCongDongCha"
            )
            SELECT "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong",
                   "CapDo", "NamBatDau", "TrangThai"
            FROM chain
            ORDER BY depth DESC
            """,
            (community_id,),
        )
        return list(cur.fetchall())


def get_descendant_ids(community_id: int, include_inactive: bool = False) -> list[int]:
    """Return IDs of community_id and all nested descendant units."""
    status_filter = "" if include_inactive else "WHERE c.\"TrangThai\" = 'DangHoatDong'"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            WITH RECURSIVE sub AS (
                SELECT "MaCongDong", "TrangThai"
                FROM "CongDong"
                WHERE "MaCongDong" = %s
                UNION ALL
                SELECT c."MaCongDong", c."TrangThai"
                FROM "CongDong" c
                JOIN sub s ON c."MaCongDongCha" = s."MaCongDong"
                {status_filter}
            )
            SELECT "MaCongDong" FROM sub ORDER BY "MaCongDong" ASC
            """,
            (community_id,),
        )
        return [int(row["MaCongDong"]) for row in cur.fetchall()]


def find_duplicate_code(
    ky_hieu: str,
    parent_id: int | None,
    cap_do: str,
    exclude_id: int | None = None,
) -> dict | None:
    """Check sibling duplicate KyHieu under the same parent and level."""
    clauses = [
        'LOWER("KyHieu") = LOWER(%s)',
        '"CapDo" = %s',
        '"MaCongDongCha" IS NULL' if parent_id is None else '"MaCongDongCha" = %s',
    ]
    params: list[object] = [ky_hieu, cap_do]
    if parent_id is not None:
        params.append(parent_id)
    if exclude_id is not None:
        clauses.append('"MaCongDong" <> %s')
        params.append(exclude_id)

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f'SELECT {_COMMUNITY_COLS} FROM "CongDong" WHERE {" AND ".join(clauses)} LIMIT 1',
            tuple(params),
        )
        return cur.fetchone()


def count_active_children(community_id: int) -> int:
    """Count direct active children under community_id."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)::int AS cnt
            FROM "CongDong"
            WHERE "MaCongDongCha" = %s AND "TrangThai" = 'DangHoatDong'
            """,
            (community_id,),
        )
        return int(cur.fetchone()["cnt"])


def create_community(data: dict) -> dict:
    """Insert a new CongDong unit and return the persisted row."""
    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                f"""
                INSERT INTO "CongDong" (
                    "MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "NamBatDau", "TrangThai"
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING {_COMMUNITY_COLS}
                """,
                (
                    data.get("MaCongDongCha"),
                    data.get("KyHieu"),
                    data["TenCongDong"],
                    data["CapDo"],
                    data.get("NamBatDau"),
                    data.get("TrangThai", "DangHoatDong"),
                ),
            )
            row = cur.fetchone()
            conn.commit()
            return row
        except psycopg.errors.Error as exc:
            conn.rollback()
            raise ValueError(str(exc)) from exc


def update_community(community_id: int, fields: dict) -> dict | None:
    """Update mutable columns on an existing CongDong unit."""
    allowed = ("MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "NamBatDau", "TrangThai")
    updates: list[str] = []
    params: list[object] = []
    for col in allowed:
        if col in fields:
            updates.append(f'"{col}" = %s')
            params.append(fields[col])
    if not updates:
        return get_community_by_id(community_id)

    params.append(community_id)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f'UPDATE "CongDong" SET {", ".join(updates)} WHERE "MaCongDong" = %s RETURNING {_COMMUNITY_COLS}',
            tuple(params),
        )
        row = cur.fetchone()
        conn.commit()
        return row


def deactivate_community(community_id: int, cascade: bool = False) -> list[dict]:
    """Soft-deactivate one CongDong node (or its entire descendant subtree)."""
    with get_conn() as conn, conn.cursor() as cur:
        if cascade:
            cur.execute(
                f"""
                WITH RECURSIVE sub AS (
                    SELECT "MaCongDong" FROM "CongDong" WHERE "MaCongDong" = %s
                    UNION ALL
                    SELECT c."MaCongDong"
                    FROM "CongDong" c
                    JOIN sub s ON c."MaCongDongCha" = s."MaCongDong"
                )
                UPDATE "CongDong"
                SET "TrangThai" = 'NgungHoatDong'
                WHERE "MaCongDong" IN (SELECT "MaCongDong" FROM sub)
                RETURNING {_COMMUNITY_COLS}
                """,
                (community_id,),
            )
            rows = list(cur.fetchall())
        else:
            cur.execute(
                f"""
                UPDATE "CongDong"
                SET "TrangThai" = 'NgungHoatDong'
                WHERE "MaCongDong" = %s
                RETURNING {_COMMUNITY_COLS}
                """,
                (community_id,),
            )
            row = cur.fetchone()
            rows = [row] if row else []
        conn.commit()
        return rows
