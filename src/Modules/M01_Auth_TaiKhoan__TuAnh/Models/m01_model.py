"""PostgreSQL Model (psycopg) cho M1: Tài khoản, Hồ sơ & Quên mật khẩu (OTP) (Nguyễn Ngô Tú Anh)."""
from __future__ import annotations

import psycopg

from src.Shared.config.db import get_conn, get_database_url

TABLES = ["NguoiDung"]

_USER_SELECT_COLS = """
    "MaNguoiDung", "MaLop", "VaiTro", "MaSinhVien", "Email",
    "MatKhauHash", "HoTen", "SoDienThoai", "AnhDaiDien", "GioiThieu",
    "CaiDatRiengTu", "MaOTP", "HanOTP", "TrangThai", "NgayTao", "NgayCapNhat"
"""

_ALLOWED_PROFILE_COLUMNS = (
    "HoTen",
    "SoDienThoai",
    "AnhDaiDien",
    "GioiThieu",
    "MaSinhVien",
    "MaLop",
    "CaiDatRiengTu",
)


def get_module_health() -> dict:
    return {
        "module": "M1",
        "owner": "Nguyễn Ngô Tú Anh",
        "tables": TABLES,
        "db_configured": bool(get_database_url()),
    }


def get_community_children(parent_id: int | None = None) -> list[dict]:
    """Fetch active CongDong nodes for a given parent_id (or root Truong nodes when None)."""
    with get_conn() as conn, conn.cursor() as cur:
        if parent_id is None:
            cur.execute(
                """
                SELECT "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "NamBatDau", "TrangThai"
                FROM "CongDong"
                WHERE "MaCongDongCha" IS NULL AND "TrangThai" = 'DangHoatDong'
                ORDER BY "TenCongDong" ASC
                """
            )
        else:
            cur.execute(
                """
                SELECT "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "NamBatDau", "TrangThai"
                FROM "CongDong"
                WHERE "MaCongDongCha" = %s AND "TrangThai" = 'DangHoatDong'
                ORDER BY "TenCongDong" ASC
                """,
                (parent_id,),
            )
        return list(cur.fetchall())


def get_active_class_by_id(lop_id: int) -> dict | None:
    """Verify that the target CongDong row is an active Lop."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "TrangThai"
            FROM "CongDong"
            WHERE "MaCongDong" = %s AND "CapDo" = 'Lop' AND "TrangThai" = 'DangHoatDong'
            """,
            (lop_id,),
        )
        return cur.fetchone()


def get_community_chain(lop_id: int) -> list[dict]:
    """Resolve the 5-level ancestor chain (Truong -> Khoa -> Nganh -> KhoaHoc -> Lop) for a Lop ID."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            WITH RECURSIVE chain AS (
                SELECT "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "NamBatDau", 0 AS depth
                FROM "CongDong"
                WHERE "MaCongDong" = %s
                UNION ALL
                SELECT p."MaCongDong", p."MaCongDongCha", p."KyHieu", p."TenCongDong", p."CapDo", p."NamBatDau", c.depth + 1
                FROM "CongDong" p
                JOIN chain c ON p."MaCongDong" = c."MaCongDongCha"
            )
            SELECT "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "NamBatDau"
            FROM chain
            ORDER BY depth DESC
            """,
            (lop_id,),
        )
        return list(cur.fetchall())


def get_user_by_email(email: str) -> dict | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f'SELECT {_USER_SELECT_COLS} FROM "NguoiDung" WHERE LOWER("Email") = LOWER(%s)',
            (email.strip(),),
        )
        return cur.fetchone()


def get_user_by_id(user_id: int) -> dict | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f'SELECT {_USER_SELECT_COLS} FROM "NguoiDung" WHERE "MaNguoiDung" = %s',
            (user_id,),
        )
        return cur.fetchone()


def create_user(data: dict) -> dict:
    """Insert a new NguoiDung row and raise explicit ValueError on email/MSSV conflicts."""
    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                f"""
                INSERT INTO "NguoiDung" (
                    "MaLop", "VaiTro", "MaSinhVien", "Email",
                    "MatKhauHash", "HoTen", "SoDienThoai", "GioiThieu"
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING {_USER_SELECT_COLS}
                """,
                (
                    data.get("MaLop"),
                    data.get("VaiTro", "SinhVien"),
                    data.get("MaSinhVien"),
                    data["Email"],
                    data["MatKhauHash"],
                    data["HoTen"],
                    data.get("SoDienThoai"),
                    data.get("GioiThieu"),
                ),
            )
            row = cur.fetchone()
            conn.commit()
            return row
        except psycopg.errors.UniqueViolation as exc:
            conn.rollback()
            cname = getattr(exc.diag, "constraint_name", "") or ""
            if "MaSinhVien" in cname:
                raise ValueError("DUPLICATE_MSSV") from exc
            raise ValueError("DUPLICATE_EMAIL") from exc


def update_password_hash(user_id: int, password_hash: str) -> bool:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "NguoiDung"
            SET "MatKhauHash" = %s, "NgayCapNhat" = NOW()
            WHERE "MaNguoiDung" = %s
            """,
            (password_hash, user_id),
        )
        updated = cur.rowcount > 0
        conn.commit()
        return updated


def save_otp(user_id: int, otp_code: str, expires_minutes: int = 10) -> dict | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            UPDATE "NguoiDung"
            SET "MaOTP" = %s,
                "HanOTP" = NOW() + make_interval(mins => %s),
                "NgayCapNhat" = NOW()
            WHERE "MaNguoiDung" = %s
            RETURNING {_USER_SELECT_COLS}
            """,
            (otp_code, expires_minutes, user_id),
        )
        row = cur.fetchone()
        conn.commit()
        return row


def reset_password_with_otp(user_id: int, new_password_hash: str) -> bool:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "NguoiDung"
            SET "MatKhauHash" = %s,
                "MaOTP" = NULL,
                "HanOTP" = NULL,
                "NgayCapNhat" = NOW()
            WHERE "MaNguoiDung" = %s
            """,
            (new_password_hash, user_id),
        )
        updated = cur.rowcount > 0
        conn.commit()
        return updated


def update_user_profile(user_id: int, fields: dict) -> dict | None:
    """Update allowlisted profile/privacy fields on NguoiDung safely."""
    updates: list[str] = []
    values: list[object] = []
    for col in _ALLOWED_PROFILE_COLUMNS:
        if col in fields:
            updates.append(f'"{col}" = %s')
            values.append(fields[col])
    if not updates:
        return get_user_by_id(user_id)

    updates.append('"NgayCapNhat" = NOW()')
    values.append(user_id)
    sql = f'UPDATE "NguoiDung" SET {", ".join(updates)} WHERE "MaNguoiDung" = %s RETURNING {_USER_SELECT_COLS}'

    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(sql, tuple(values))
            row = cur.fetchone()
            conn.commit()
            return row
        except psycopg.errors.UniqueViolation as exc:
            conn.rollback()
            raise ValueError("DUPLICATE_MSSV") from exc
