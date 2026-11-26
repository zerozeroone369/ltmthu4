"""PostgreSQL Model (psycopg) cho M3: Bài viết, Tương tác & Kết bạn (Duy)."""
from __future__ import annotations

import psycopg

from src.Shared.config.db import get_conn, get_database_url

TABLES = ["BaiViet", "BinhLuan", "TuongTac", "KetBan"]


def get_module_health() -> dict:
    return {
        "module": "M3",
        "owner": "Duy",
        "tables": TABLES,
        "db_configured": bool(get_database_url()),
    }


def get_active_community_by_id(community_id: int) -> dict | None:
    """Verify target CongDong exists and is active."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaCongDong", "MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "TrangThai"
            FROM "CongDong"
            WHERE "MaCongDong" = %s AND "TrangThai" = 'DangHoatDong'
            """,
            (community_id,),
        )
        return cur.fetchone()


def get_user_basic(user_id: int) -> dict | None:
    """Load basic active status and privacy metadata for a user."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaNguoiDung", "MaLop", "VaiTro", "MaSinhVien", "Email",
                   "HoTen", "SoDienThoai", "AnhDaiDien", "GioiThieu",
                   "CaiDatRiengTu", "TrangThai"
            FROM "NguoiDung"
            WHERE "MaNguoiDung" = %s
            """,
            (user_id,),
        )
        return cur.fetchone()


def get_relationship_between(user_a: int, user_b: int) -> dict | None:
    """Return bidirectional KetBan row between user_a and user_b if present."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaKetBan", "MaNguoiGui", "MaNguoiNhan", "TrangThai", "NgayTao", "NgayCapNhat"
            FROM "KetBan"
            WHERE ("MaNguoiGui" = %s AND "MaNguoiNhan" = %s)
               OR ("MaNguoiGui" = %s AND "MaNguoiNhan" = %s)
            LIMIT 1
            """,
            (user_a, user_b, user_b, user_a),
        )
        return cur.fetchone()


def get_blocked_user_ids(user_id: int) -> set[int]:
    """Return user IDs that block or are blocked by user_id."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaNguoiGui", "MaNguoiNhan"
            FROM "KetBan"
            WHERE "TrangThai" = 'DaChan'
              AND ("MaNguoiGui" = %s OR "MaNguoiNhan" = %s)
            """,
            (user_id, user_id),
        )
        blocked: set[int] = set()
        for row in cur.fetchall():
            other = int(row["MaNguoiNhan"]) if int(row["MaNguoiGui"]) == user_id else int(row["MaNguoiGui"])
            blocked.add(other)
        return blocked


def get_friend_user_ids(user_id: int) -> set[int]:
    """Return accepted friend user IDs for user_id."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaNguoiGui", "MaNguoiNhan"
            FROM "KetBan"
            WHERE "TrangThai" = 'BanBe'
              AND ("MaNguoiGui" = %s OR "MaNguoiNhan" = %s)
            """,
            (user_id, user_id),
        )
        friends: set[int] = set()
        for row in cur.fetchall():
            other = int(row["MaNguoiNhan"]) if int(row["MaNguoiGui"]) == user_id else int(row["MaNguoiGui"])
            friends.add(other)
        return friends


def list_posts(
    *,
    cong_dong_id: int | None = None,
    danh_muc: str | None = None,
    search: str = "",
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """List active BaiViet rows joined with author and CongDong display fields."""
    clauses: list[str] = ['b."TrangThai" = %s', 'u."TrangThai" = %s']
    params: list[object] = ["HienThi", "HoatDong"]

    if cong_dong_id is not None:
        clauses.append('b."MaCongDong" = %s')
        params.append(cong_dong_id)
    if danh_muc:
        clauses.append('b."DanhMuc" = %s')
        params.append(danh_muc)
    if search.strip():
        clauses.append('(b."NoiDung" ILIKE %s OR u."HoTen" ILIKE %s)')
        pattern = f"%{search.strip()}%"
        params.extend([pattern, pattern])

    where_sql = " AND ".join(clauses)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT b."MaBaiViet", b."MaNguoiDung", b."MaCongDong", b."DanhMuc",
                   b."NoiDung", b."TepDinhKem", b."SoLuotThich", b."SoBinhLuan",
                   b."TrangThai", b."NgayTao", b."NgayCapNhat",
                   u."HoTen" AS "TenTacGia", u."CaiDatRiengTu" AS "TacGiaRiengTu",
                   cd."TenCongDong", cd."CapDo"
            FROM "BaiViet" b
            JOIN "NguoiDung" u ON u."MaNguoiDung" = b."MaNguoiDung"
            JOIN "CongDong" cd ON cd."MaCongDong" = b."MaCongDong"
            WHERE {where_sql}
            ORDER BY b."NgayTao" DESC, b."MaBaiViet" DESC
            LIMIT %s OFFSET %s
            """,
            (*params, limit, offset),
        )
        return list(cur.fetchall())


def get_post_by_id(post_id: int) -> dict | None:
    """Fetch a single BaiViet joined with author and community info."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT b."MaBaiViet", b."MaNguoiDung", b."MaCongDong", b."DanhMuc",
                   b."NoiDung", b."TepDinhKem", b."SoLuotThich", b."SoBinhLuan",
                   b."TrangThai", b."NgayTao", b."NgayCapNhat",
                   u."HoTen" AS "TenTacGia", u."CaiDatRiengTu" AS "TacGiaRiengTu",
                   cd."TenCongDong", cd."CapDo"
            FROM "BaiViet" b
            JOIN "NguoiDung" u ON u."MaNguoiDung" = b."MaNguoiDung"
            JOIN "CongDong" cd ON cd."MaCongDong" = b."MaCongDong"
            WHERE b."MaBaiViet" = %s
            """,
            (post_id,),
        )
        return cur.fetchone()


def get_liked_post_ids(user_id: int, post_ids: list[int]) -> set[int]:
    """Return subset of post_ids liked by user_id."""
    if not post_ids:
        return set()
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaBaiViet"
            FROM "TuongTac"
            WHERE "MaNguoiDung" = %s AND "MaBaiViet" = ANY(%s)
            """,
            (user_id, post_ids),
        )
        return {int(row["MaBaiViet"]) for row in cur.fetchall()}


def create_post(
    *,
    user_id: int,
    cong_dong_id: int,
    danh_muc: str,
    noi_dung: str,
    tep_dinh_kem: str | None = None,
) -> dict:
    """Insert a new BaiViet row and return enriched post dict."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO "BaiViet" ("MaNguoiDung", "MaCongDong", "DanhMuc", "NoiDung", "TepDinhKem")
            VALUES (%s, %s, %s, %s, %s)
            RETURNING "MaBaiViet"
            """,
            (user_id, cong_dong_id, danh_muc, noi_dung, tep_dinh_kem),
        )
        post_id = int(cur.fetchone()["MaBaiViet"])
        conn.commit()
    return get_post_by_id(post_id)


def update_post(post_id: int, fields: dict) -> dict | None:
    """Update mutable columns of an existing BaiViet row."""
    allowed = ("MaCongDong", "DanhMuc", "NoiDung", "TepDinhKem")
    updates: list[str] = []
    params: list[object] = []
    for col in allowed:
        if col in fields:
            updates.append(f'"{col}" = %s')
            params.append(fields[col])
    if not updates:
        return get_post_by_id(post_id)

    updates.append('"NgayCapNhat" = NOW()')
    params.append(post_id)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f'UPDATE "BaiViet" SET {", ".join(updates)} WHERE "MaBaiViet" = %s RETURNING "MaBaiViet"',
            tuple(params),
        )
        row = cur.fetchone()
        conn.commit()
    return get_post_by_id(post_id) if row else None


def soft_delete_post(post_id: int) -> bool:
    """Soft-delete a post by setting TrangThai = 'DaXoa'."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "BaiViet"
            SET "TrangThai" = 'DaXoa', "NgayCapNhat" = NOW()
            WHERE "MaBaiViet" = %s AND "TrangThai" = 'HienThi'
            """,
            (post_id,),
        )
        updated = cur.rowcount > 0
        conn.commit()
        return updated


def list_comments(post_id: int) -> list[dict]:
    """List visible comments on a post ordered oldest-first."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT c."MaBinhLuan", c."MaBaiViet", c."MaNguoiDung", c."NoiDung",
                   c."TrangThai", c."NgayTao", u."HoTen" AS "TenNguoiBinhLuan"
            FROM "BinhLuan" c
            JOIN "NguoiDung" u ON u."MaNguoiDung" = c."MaNguoiDung"
            WHERE c."MaBaiViet" = %s AND c."TrangThai" = 'HienThi'
            ORDER BY c."NgayTao" ASC, c."MaBinhLuan" ASC
            """,
            (post_id,),
        )
        return list(cur.fetchall())


def get_comment_by_id(comment_id: int) -> dict | None:
    """Fetch a single BinhLuan row with author info."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT c."MaBinhLuan", c."MaBaiViet", c."MaNguoiDung", c."NoiDung",
                   c."TrangThai", c."NgayTao", u."HoTen" AS "TenNguoiBinhLuan"
            FROM "BinhLuan" c
            JOIN "NguoiDung" u ON u."MaNguoiDung" = c."MaNguoiDung"
            WHERE c."MaBinhLuan" = %s
            """,
            (comment_id,),
        )
        return cur.fetchone()


def create_comment_with_count(
    *,
    post_id: int,
    user_id: int,
    noi_dung: str,
    notification: dict | None = None,
) -> dict:
    """Insert a comment, increment BaiViet.SoBinhLuan, and store optional notification."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO "BinhLuan" ("MaBaiViet", "MaNguoiDung", "NoiDung")
            VALUES (%s, %s, %s)
            RETURNING "MaBinhLuan"
            """,
            (post_id, user_id, noi_dung),
        )
        comment_id = int(cur.fetchone()["MaBinhLuan"])
        cur.execute(
            """
            UPDATE "BaiViet"
            SET "SoBinhLuan" = "SoBinhLuan" + 1
            WHERE "MaBaiViet" = %s
            """,
            (post_id,),
        )
        if notification:
            _insert_notification_tx(cur, notification)
        conn.commit()
    return get_comment_by_id(comment_id)


def soft_delete_comment_with_count(post_id: int, comment_id: int) -> bool:
    """Soft-delete comment and decrement SoBinhLuan safely."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "BinhLuan"
            SET "TrangThai" = 'DaXoa'
            WHERE "MaBinhLuan" = %s AND "MaBaiViet" = %s AND "TrangThai" = 'HienThi'
            """,
            (comment_id, post_id),
        )
        if cur.rowcount == 0:
            conn.rollback()
            return False
        cur.execute(
            """
            UPDATE "BaiViet"
            SET "SoBinhLuan" = GREATEST(0, "SoBinhLuan" - 1)
            WHERE "MaBaiViet" = %s
            """,
            (post_id,),
        )
        conn.commit()
        return True


def toggle_post_like(
    *,
    post_id: int,
    user_id: int,
    notification: dict | None = None,
) -> dict:
    """Toggle a unique like in TuongTac and keep BaiViet.SoLuotThich in sync."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM "TuongTac"
            WHERE "MaBaiViet" = %s AND "MaNguoiDung" = %s
            RETURNING "MaTuongTac"
            """,
            (post_id, user_id),
        )
        removed = cur.fetchone()
        if removed:
            cur.execute(
                """
                UPDATE "BaiViet"
                SET "SoLuotThich" = GREATEST(0, "SoLuotThich" - 1)
                WHERE "MaBaiViet" = %s
                RETURNING "SoLuotThich"
                """,
                (post_id,),
            )
            likes = int(cur.fetchone()["SoLuotThich"])
            conn.commit()
            return {"liked": False, "so_luot_thich": likes, "notification": None}

        cur.execute(
            """
            INSERT INTO "TuongTac" ("MaBaiViet", "MaNguoiDung", "LoaiTuongTac")
            VALUES (%s, %s, 'Thich')
            """,
            (post_id, user_id),
        )
        cur.execute(
            """
            UPDATE "BaiViet"
            SET "SoLuotThich" = "SoLuotThich" + 1
            WHERE "MaBaiViet" = %s
            RETURNING "SoLuotThich"
            """,
            (post_id,),
        )
        likes = int(cur.fetchone()["SoLuotThich"])
        if notification:
            _insert_notification_tx(cur, notification)
        conn.commit()
        return {"liked": True, "so_luot_thich": likes, "notification": notification}


def search_students(
    *,
    viewer_id: int,
    query: str = "",
    lop_id: int | None = None,
    limit: int = 30,
) -> list[dict]:
    """Search active students excluding self with class label and KetBan relation info."""
    clauses = ['u."TrangThai" = %s', 'u."MaNguoiDung" <> %s']
    params: list[object] = ["HoatDong", viewer_id]

    if lop_id is not None:
        clauses.append('u."MaLop" = %s')
        params.append(lop_id)
    if query.strip():
        pattern = f"%{query.strip()}%"
        clauses.append('(u."HoTen" ILIKE %s OR COALESCE(u."MaSinhVien", \'\') ILIKE %s OR u."Email" ILIKE %s)')
        params.extend([pattern, pattern, pattern])

    where_sql = " AND ".join(clauses)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT u."MaNguoiDung", u."MaLop", cd."TenCongDong" AS "TenLop",
                   u."MaSinhVien", u."Email", u."HoTen", u."SoDienThoai",
                   u."AnhDaiDien", u."GioiThieu", u."CaiDatRiengTu",
                   kb."MaKetBan", kb."MaNguoiGui", kb."MaNguoiNhan", kb."TrangThai" AS "TrangThaiKetBan"
            FROM "NguoiDung" u
            LEFT JOIN "CongDong" cd ON cd."MaCongDong" = u."MaLop"
            LEFT JOIN "KetBan" kb ON (
                (kb."MaNguoiGui" = %s AND kb."MaNguoiNhan" = u."MaNguoiDung")
                OR (kb."MaNguoiGui" = u."MaNguoiDung" AND kb."MaNguoiNhan" = %s)
            )
            WHERE {where_sql}
              AND COALESCE(kb."TrangThai", '') <> 'DaChan'
            ORDER BY u."HoTen" ASC, u."MaNguoiDung" ASC
            LIMIT %s
            """,
            (viewer_id, viewer_id, *params, limit),
        )
        return list(cur.fetchall())


def list_friend_relations(user_id: int) -> list[dict]:
    """List pending and accepted KetBan entries involving user_id."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT kb."MaKetBan", kb."MaNguoiGui", kb."MaNguoiNhan", kb."TrangThai",
                   kb."NgayTao", kb."NgayCapNhat",
                   peer."MaNguoiDung" AS "PeerId", peer."HoTen" AS "PeerHoTen",
                   peer."MaSinhVien" AS "PeerMaSinhVien", peer."Email" AS "PeerEmail",
                   peer."SoDienThoai" AS "PeerSoDienThoai", peer."CaiDatRiengTu" AS "PeerRiengTu",
                   peer."MaLop" AS "PeerMaLop", cd."TenCongDong" AS "PeerTenLop"
            FROM "KetBan" kb
            JOIN "NguoiDung" peer ON peer."MaNguoiDung" = CASE
                WHEN kb."MaNguoiGui" = %s THEN kb."MaNguoiNhan"
                ELSE kb."MaNguoiGui"
            END
            LEFT JOIN "CongDong" cd ON cd."MaCongDong" = peer."MaLop"
            WHERE (kb."MaNguoiGui" = %s OR kb."MaNguoiNhan" = %s)
              AND kb."TrangThai" IN ('ChoDuyet', 'BanBe')
              AND peer."TrangThai" = 'HoatDong'
            ORDER BY kb."NgayTao" DESC, kb."MaKetBan" DESC
            """,
            (user_id, user_id, user_id),
        )
        return list(cur.fetchall())


def get_friendship_by_id(friendship_id: int) -> dict | None:
    """Fetch a KetBan row by primary key."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT "MaKetBan", "MaNguoiGui", "MaNguoiNhan", "TrangThai", "NgayTao", "NgayCapNhat"
            FROM "KetBan"
            WHERE "MaKetBan" = %s
            """,
            (friendship_id,),
        )
        return cur.fetchone()


def upsert_friend_request(
    *,
    sender_id: int,
    target_id: int,
    existing_id: int | None = None,
    notification: dict | None = None,
) -> dict:
    """Insert a fresh ChoDuyet request or reactivate a previously rejected KetBan row."""
    with get_conn() as conn, conn.cursor() as cur:
        try:
            if existing_id is not None:
                cur.execute(
                    """
                    UPDATE "KetBan"
                    SET "MaNguoiGui" = %s, "MaNguoiNhan" = %s,
                        "TrangThai" = 'ChoDuyet', "NgayCapNhat" = NOW()
                    WHERE "MaKetBan" = %s
                    RETURNING "MaKetBan", "MaNguoiGui", "MaNguoiNhan", "TrangThai", "NgayTao", "NgayCapNhat"
                    """,
                    (sender_id, target_id, existing_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO "KetBan" ("MaNguoiGui", "MaNguoiNhan", "TrangThai")
                    VALUES (%s, %s, 'ChoDuyet')
                    RETURNING "MaKetBan", "MaNguoiGui", "MaNguoiNhan", "TrangThai", "NgayTao", "NgayCapNhat"
                    """,
                    (sender_id, target_id),
                )
            row = cur.fetchone()
            if notification:
                _insert_notification_tx(cur, notification)
            conn.commit()
            return row
        except psycopg.errors.UniqueViolation as exc:
            conn.rollback()
            raise ValueError("DUPLICATE_FRIEND_REQUEST") from exc


def update_friendship_status(
    *,
    friendship_id: int,
    trang_thai: str,
    notification: dict | None = None,
) -> dict | None:
    """Update KetBan status ('BanBe' or 'TuChoi') and optionally store a notification."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE "KetBan"
            SET "TrangThai" = %s, "NgayCapNhat" = NOW()
            WHERE "MaKetBan" = %s
            RETURNING "MaKetBan", "MaNguoiGui", "MaNguoiNhan", "TrangThai", "NgayTao", "NgayCapNhat"
            """,
            (trang_thai, friendship_id),
        )
        row = cur.fetchone()
        if row and notification:
            _insert_notification_tx(cur, notification)
        conn.commit()
        return row


def delete_friendship(friendship_id: int) -> bool:
    """Remove a pending or accepted friendship row."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM "KetBan"
            WHERE "MaKetBan" = %s AND "TrangThai" IN ('ChoDuyet', 'BanBe', 'TuChoi')
            """,
            (friendship_id,),
        )
        deleted = cur.rowcount > 0
        conn.commit()
        return deleted


def _insert_notification_tx(cur, notif: dict) -> None:
    cur.execute(
        """
        INSERT INTO "ThongBao" ("MaNguoiNhan", "MaNguoiThucHien", "LoaiThongBao", "NoiDung", "LienKet")
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
