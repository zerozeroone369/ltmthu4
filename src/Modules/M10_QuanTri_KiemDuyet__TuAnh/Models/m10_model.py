"""PostgreSQL Model (psycopg) cho M10: Quản trị Hệ thống & Kiểm duyệt (Admin) (Nguyễn Ngô Tú Anh)."""
from __future__ import annotations

from src.Shared.config.db import get_conn, get_database_url

TABLES = ["BaoCaoViPham", "NguoiDung"]

# Static allowlist mapping report content types to actual schema identifiers.
CONTENT_TARGETS: dict[str, dict[str, str | None]] = {
    "BaiViet": {"table": "BaiViet", "pk": "MaBaiViet", "owner_col": "MaNguoiDung", "status_col": "TrangThai", "preview_col": "NoiDung"},
    "BinhLuan": {"table": "BinhLuan", "pk": "MaBinhLuan", "owner_col": "MaNguoiDung", "status_col": "TrangThai", "preview_col": "NoiDung"},
    "TaiLieu": {"table": "TaiLieu", "pk": "MaTaiLieu", "owner_col": "MaNguoiDung", "status_col": "TrangThai", "preview_col": "TieuDe"},
    "CauHoi": {"table": "CauHoi", "pk": "MaCauHoi", "owner_col": "MaNguoiDung", "status_col": "TrangThai", "preview_col": "TieuDe"},
    "CauTraLoi": {"table": "CauTraLoi", "pk": "MaCauTraLoi", "owner_col": "MaNguoiDung", "status_col": None, "preview_col": "NoiDung"},
    "TinTruong": {"table": "TinTruong", "pk": "MaTinTruong", "owner_col": "MaQuanTriVien", "status_col": "TrangThai", "preview_col": "TieuDe"},
    "NhomHoc": {"table": "NhomHoc", "pk": "MaNhomHoc", "owner_col": "MaTruongNhom", "status_col": "TrangThai", "preview_col": "TenNhom"},
    "NguoiDung": {"table": "NguoiDung", "pk": "MaNguoiDung", "owner_col": "MaNguoiDung", "status_col": "TrangThai", "preview_col": "HoTen"},
}

_ADMIN_USER_COLS = """
    u."MaNguoiDung", u."MaLop", cd."TenCongDong" AS "TenLop",
    u."VaiTro", u."MaSinhVien", u."Email", u."HoTen",
    u."SoDienThoai", u."TrangThai", u."NgayTao", u."NgayCapNhat"
"""


def get_module_health() -> dict:
    return {
        "module": "M10",
        "owner": "Nguyễn Ngô Tú Anh",
        "tables": TABLES,
        "db_configured": bool(get_database_url()),
    }


def list_users(
    *,
    search: str = "",
    vai_tro: str | None = None,
    trang_thai: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    clauses: list[str] = []
    params: list[object] = []

    if search.strip():
        pattern = f"%{search.strip()}%"
        clauses.append('(u."HoTen" ILIKE %s OR u."Email" ILIKE %s OR COALESCE(u."MaSinhVien", \'\') ILIKE %s)')
        params.extend([pattern, pattern, pattern])
    if vai_tro:
        clauses.append('u."VaiTro" = %s')
        params.append(vai_tro)
    if trang_thai:
        clauses.append('u."TrangThai" = %s')
        params.append(trang_thai)

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f'SELECT COUNT(*)::int AS total FROM "NguoiDung" u {where_sql}',
            tuple(params),
        )
        total = cur.fetchone()["total"]

        cur.execute(
            f"""
            SELECT {_ADMIN_USER_COLS}
            FROM "NguoiDung" u
            LEFT JOIN "CongDong" cd ON cd."MaCongDong" = u."MaLop"
            {where_sql}
            ORDER BY u."MaNguoiDung" DESC
            LIMIT %s OFFSET %s
            """,
            (*params, limit, offset),
        )
        items = list(cur.fetchall())

        cur.execute(
            """
            SELECT
                COUNT(*)::int AS total_users,
                COUNT(*) FILTER (WHERE "VaiTro" = 'QuanTriVien' AND "TrangThai" = 'HoatDong')::int AS active_admins,
                COUNT(*) FILTER (WHERE "TrangThai" <> 'HoatDong')::int AS locked_users
            FROM "NguoiDung"
            """
        )
        stats = cur.fetchone()

    return {"items": items, "total": total, "stats": stats}


def get_user_by_id(user_id: int) -> dict | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT {_ADMIN_USER_COLS}
            FROM "NguoiDung" u
            LEFT JOIN "CongDong" cd ON cd."MaCongDong" = u."MaLop"
            WHERE u."MaNguoiDung" = %s
            """,
            (user_id,),
        )
        return cur.fetchone()


def count_active_admins() -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)::int AS cnt
            FROM "NguoiDung"
            WHERE "VaiTro" = 'QuanTriVien' AND "TrangThai" = 'HoatDong'
            """
        )
        return int(cur.fetchone()["cnt"])


def update_user_lock_status(user_id: int, trang_thai: str) -> dict | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "NguoiDung"
            SET "TrangThai" = %s, "NgayCapNhat" = NOW()
            WHERE "MaNguoiDung" = %s
            RETURNING "MaNguoiDung"
            """,
            (trang_thai, user_id),
        )
        row = cur.fetchone()
        conn.commit()
    return get_user_by_id(user_id) if row else None


def update_user_role(user_id: int, vai_tro: str) -> dict | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "NguoiDung"
            SET "VaiTro" = %s, "NgayCapNhat" = NOW()
            WHERE "MaNguoiDung" = %s
            RETURNING "MaNguoiDung"
            """,
            (vai_tro, user_id),
        )
        row = cur.fetchone()
        conn.commit()
    return get_user_by_id(user_id) if row else None


def get_content_target(loai_noi_dung: str, id_noi_dung: int) -> dict | None:
    """Look up target row existence, owner ID, status, and preview from allowlisted table."""
    meta = CONTENT_TARGETS.get(loai_noi_dung)
    if not meta:
        return None
    table = meta["table"]
    pk = meta["pk"]
    owner_col = meta["owner_col"]
    status_col = meta["status_col"]
    preview_col = meta["preview_col"]

    status_expr = f'"{status_col}"' if status_col else "NULL::varchar"
    sql = (
        f'SELECT "{pk}" AS id, "{owner_col}" AS owner_id, '
        f'{status_expr} AS status, "{preview_col}" AS preview '
        f'FROM "{table}" WHERE "{pk}" = %s'
    )
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (id_noi_dung,))
        return cur.fetchone()


def create_report(
    reporter_id: int,
    loai_noi_dung: str,
    id_noi_dung: int,
    ly_do: str,
    chi_tiet: str | None,
) -> dict:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO "BaoCaoViPham" (
                "MaNguoiBaoCao", "LoaiNoiDung", "IdNoiDung", "LyDo", "ChiTiet"
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING "MaBaoCao"
            """,
            (reporter_id, loai_noi_dung, id_noi_dung, ly_do, chi_tiet),
        )
        report_id = cur.fetchone()["MaBaoCao"]
        conn.commit()
    return get_report_by_id(report_id)


def list_reports(
    *,
    trang_thai: str | None = None,
    loai_noi_dung: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    clauses: list[str] = []
    params: list[object] = []
    if trang_thai:
        clauses.append('bc."TrangThai" = %s')
        params.append(trang_thai)
    if loai_noi_dung:
        clauses.append('bc."LoaiNoiDung" = %s')
        params.append(loai_noi_dung)

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f'SELECT COUNT(*)::int AS total FROM "BaoCaoViPham" bc {where_sql}', tuple(params))
        total = cur.fetchone()["total"]

        cur.execute(
            f"""
            SELECT
                bc."MaBaoCao", bc."MaNguoiBaoCao",
                rep."HoTen" AS "TenNguoiBaoCao", rep."Email" AS "EmailNguoiBaoCao",
                bc."MaAdminXuLy", adm."HoTen" AS "TenAdminXuLy",
                bc."LoaiNoiDung", bc."IdNoiDung", bc."LyDo", bc."ChiTiet",
                bc."TrangThai", bc."QuyetDinh", bc."GhiChuXuLy",
                bc."NgayGui", bc."NgayXuLy"
            FROM "BaoCaoViPham" bc
            JOIN "NguoiDung" rep ON rep."MaNguoiDung" = bc."MaNguoiBaoCao"
            LEFT JOIN "NguoiDung" adm ON adm."MaNguoiDung" = bc."MaAdminXuLy"
            {where_sql}
            ORDER BY
                CASE WHEN bc."TrangThai" = 'ChoDuyet' THEN 0 ELSE 1 END,
                bc."NgayGui" DESC,
                bc."MaBaoCao" DESC
            LIMIT %s OFFSET %s
            """,
            (*params, limit, offset),
        )
        items = list(cur.fetchall())

        cur.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE "TrangThai" = 'ChoDuyet')::int AS cho_duyet,
                COUNT(*) FILTER (WHERE "TrangThai" = 'DaXuLy')::int AS da_xu_ly,
                COUNT(*) FILTER (WHERE "TrangThai" = 'TuChoi')::int AS tu_choi
            FROM "BaoCaoViPham"
            """
        )
        stats = cur.fetchone()

    return {"items": items, "total": total, "stats": stats}


def get_report_by_id(report_id: int) -> dict | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                bc."MaBaoCao", bc."MaNguoiBaoCao",
                rep."HoTen" AS "TenNguoiBaoCao", rep."Email" AS "EmailNguoiBaoCao",
                bc."MaAdminXuLy", adm."HoTen" AS "TenAdminXuLy",
                bc."LoaiNoiDung", bc."IdNoiDung", bc."LyDo", bc."ChiTiet",
                bc."TrangThai", bc."QuyetDinh", bc."GhiChuXuLy",
                bc."NgayGui", bc."NgayXuLy"
            FROM "BaoCaoViPham" bc
            JOIN "NguoiDung" rep ON rep."MaNguoiDung" = bc."MaNguoiBaoCao"
            LEFT JOIN "NguoiDung" adm ON adm."MaNguoiDung" = bc."MaAdminXuLy"
            WHERE bc."MaBaoCao" = %s
            """,
            (report_id,),
        )
        return cur.fetchone()


def resolve_report_transaction(
    *,
    report_id: int,
    admin_id: int,
    quyet_dinh: str,
    ghi_chu_xu_ly: str | None,
    report_status: str,
    content_status: str | None,
    lock_owner_id: int | None,
    notifications: list[dict],
) -> dict:
    """Atomically update BaoCaoViPham, target content/account status, and insert ThongBao rows."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT "MaBaoCao", "LoaiNoiDung", "IdNoiDung"
                FROM "BaoCaoViPham"
                WHERE "MaBaoCao" = %s
                FOR UPDATE
                """,
                (report_id,),
            )
            report_row = cur.fetchone()
            if not report_row:
                raise LookupError("REPORT_NOT_FOUND")

            if content_status:
                meta = CONTENT_TARGETS.get(report_row["LoaiNoiDung"])
                if meta and meta["status_col"]:
                    cur.execute(
                        f'UPDATE "{meta["table"]}" SET "{meta["status_col"]}" = %s WHERE "{meta["pk"]}" = %s',
                        (content_status, report_row["IdNoiDung"]),
                    )

            if lock_owner_id is not None:
                cur.execute(
                    """
                    UPDATE "NguoiDung"
                    SET "TrangThai" = 'BiKhoa', "NgayCapNhat" = NOW()
                    WHERE "MaNguoiDung" = %s
                    """,
                    (lock_owner_id,),
                )

            cur.execute(
                """
                UPDATE "BaoCaoViPham"
                SET "TrangThai" = %s,
                    "QuyetDinh" = %s,
                    "MaAdminXuLy" = %s,
                    "GhiChuXuLy" = %s,
                    "NgayXuLy" = NOW()
                WHERE "MaBaoCao" = %s
                """,
                (report_status, quyet_dinh, admin_id, ghi_chu_xu_ly, report_id),
            )

            for notif in notifications:
                cur.execute(
                    """
                    INSERT INTO "ThongBao" (
                        "MaNguoiNhan", "MaNguoiThucHien", "LoaiThongBao", "NoiDung", "LienKet"
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        notif["MaNguoiNhan"],
                        notif.get("MaNguoiThucHien"),
                        notif["LoaiThongBao"],
                        notif["NoiDung"],
                        notif.get("LienKet"),
                    ),
                )

        conn.commit()

    return get_report_by_id(report_id)
