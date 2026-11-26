"""Business logic cho M3: Bài viết, Tương tác (Like/Comment) & Kết bạn (Duy)."""
from __future__ import annotations

import asyncio
import json

from fastapi import HTTPException

from src.Shared.middlewares.realtime_helper import manager

from ..Models import m03_model as model

VALID_POST_CATEGORIES = {"HocTap", "ChiaSe", "ThaoLuan", "HoiDap", "Khac"}


def _push_realtime_best_effort(notification: dict | None) -> None:
    """Dispatch WebSocket notification if an asyncio event loop is active."""
    if not notification:
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(
        manager.send_notification(
            str(notification["MaNguoiNhan"]),
            "notification",
            {
                "type": notification["LoaiThongBao"],
                "content": notification["NoiDung"],
                "link": notification.get("LienKet"),
            },
        )
    )


def _parse_privacy(raw: str | dict | None) -> dict:
    defaults = {"hienSdt": "BanBe", "hienEmail": "CongDong", "hienBaiViet": "CongDong"}
    if isinstance(raw, dict):
        return {**defaults, **raw}
    if isinstance(raw, str) and raw.strip():
        try:
            loaded = json.loads(raw)
            if isinstance(loaded, dict):
                return {**defaults, **loaded}
        except json.JSONDecodeError:
            pass
    return defaults


def _can_view_author_post(author_id: int, author_privacy: str | dict | None, viewer_id: int, blocked_ids: set[int], friend_ids: set[int]) -> bool:
    if viewer_id == author_id:
        return True
    if author_id in blocked_ids:
        return False
    scope = _parse_privacy(author_privacy).get("hienBaiViet", "CongDong")
    if scope == "ChiMinhToi":
        return False
    if scope == "BanBe":
        return author_id in friend_ids
    return True


def _mask_contact_field(value: str | None, scope: str, *, is_self: bool, is_friend: bool) -> str | None:
    if not value:
        return None
    if is_self or scope == "CongDong":
        return value
    if scope == "BanBe" and is_friend:
        return value
    return None


def _clean_post_content(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Nội dung bài viết không được để trống.")
    return cleaned


def _clean_category(danh_muc: str | None) -> str:
    cat = (danh_muc or "HocTap").strip()
    if cat not in VALID_POST_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Danh mục phải thuộc {sorted(VALID_POST_CATEGORIES)}.",
        )
    return cat


def _clean_attachment(path: str | None) -> str | None:
    if path is None:
        return None
    cleaned = path.strip()
    if not cleaned:
        return None
    if len(cleaned) > 500:
        raise HTTPException(status_code=400, detail="Đường dẫn tệp đính kèm tối đa 500 ký tự.")
    return cleaned


def _serialize_post(post: dict, *, liked: bool) -> dict:
    item = dict(post)
    item.pop("TacGiaRiengTu", None)
    item["liked_by_me"] = liked
    return item


def _require_visible_post(post_id: int, viewer_id: int) -> dict:
    post = model.get_post_by_id(post_id)
    if not post or post.get("TrangThai") != "HienThi":
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết hoặc bài viết đã bị ẩn/xóa.")
    blocked = model.get_blocked_user_ids(viewer_id)
    friends = model.get_friend_user_ids(viewer_id)
    if not _can_view_author_post(
        int(post["MaNguoiDung"]),
        post.get("TacGiaRiengTu"),
        viewer_id,
        blocked,
        friends,
    ):
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem bài viết này theo cài đặt riêng tư hoặc chặn.")
    return post


def list_posts(
    *,
    viewer_id: int,
    cong_dong_id: int | None = None,
    danh_muc: str | None = None,
    search: str = "",
    limit: int = 30,
    offset: int = 0,
) -> dict:
    if danh_muc:
        danh_muc = _clean_category(danh_muc)

    rows = model.list_posts(
        cong_dong_id=cong_dong_id,
        danh_muc=danh_muc,
        search=search,
        limit=limit,
        offset=offset,
    )
    blocked = model.get_blocked_user_ids(viewer_id)
    friends = model.get_friend_user_ids(viewer_id)
    visible = [
        row
        for row in rows
        if _can_view_author_post(int(row["MaNguoiDung"]), row.get("TacGiaRiengTu"), viewer_id, blocked, friends)
    ]
    liked_ids = model.get_liked_post_ids(viewer_id, [int(r["MaBaiViet"]) for r in visible])
    items = [_serialize_post(row, liked=int(row["MaBaiViet"]) in liked_ids) for row in visible]
    return {"items": items, "total": len(items)}


def get_post_detail(*, post_id: int, viewer_id: int) -> dict:
    post = _require_visible_post(post_id, viewer_id)
    liked_ids = model.get_liked_post_ids(viewer_id, [post_id])
    return {"post": _serialize_post(post, liked=post_id in liked_ids)}


def create_post(
    *,
    user_id: int,
    cong_dong_id: int,
    noi_dung: str,
    danh_muc: str = "HocTap",
    tep_dinh_kem: str | None = None,
) -> dict:
    community = model.get_active_community_by_id(cong_dong_id)
    if not community:
        raise HTTPException(status_code=404, detail="Cộng đồng không tồn tại hoặc đã ngừng hoạt động.")

    created = model.create_post(
        user_id=user_id,
        cong_dong_id=cong_dong_id,
        danh_muc=_clean_category(danh_muc),
        noi_dung=_clean_post_content(noi_dung),
        tep_dinh_kem=_clean_attachment(tep_dinh_kem),
    )
    return {
        "ok": True,
        "message": "Đã đăng bài viết mới lên cộng đồng.",
        "post": _serialize_post(created, liked=False),
    }


def update_post(
    *,
    post_id: int,
    user_id: int,
    noi_dung: str | None = None,
    danh_muc: str | None = None,
    cong_dong_id: int | None = None,
    tep_dinh_kem: str | None = None,
    tep_dinh_kem_provided: bool = False,
) -> dict:
    existing = model.get_post_by_id(post_id)
    if not existing or existing.get("TrangThai") != "HienThi":
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    if int(existing["MaNguoiDung"]) != user_id:
        raise HTTPException(status_code=403, detail="Chỉ tác giả mới có quyền chỉnh sửa bài viết của mình.")

    fields: dict[str, object] = {}
    if noi_dung is not None:
        fields["NoiDung"] = _clean_post_content(noi_dung)
    if danh_muc is not None:
        fields["DanhMuc"] = _clean_category(danh_muc)
    if cong_dong_id is not None:
        community = model.get_active_community_by_id(cong_dong_id)
        if not community:
            raise HTTPException(status_code=404, detail="Cộng đồng mới không tồn tại hoặc đã ngừng hoạt động.")
        fields["MaCongDong"] = cong_dong_id
    if tep_dinh_kem_provided:
        fields["TepDinhKem"] = _clean_attachment(tep_dinh_kem)

    updated = model.update_post(post_id, fields)
    liked_ids = model.get_liked_post_ids(user_id, [post_id])
    return {
        "ok": True,
        "message": "Đã cập nhật bài viết.",
        "post": _serialize_post(updated, liked=post_id in liked_ids),
    }


def delete_post(*, post_id: int, user_id: int) -> dict:
    existing = model.get_post_by_id(post_id)
    if not existing or existing.get("TrangThai") != "HienThi":
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    if int(existing["MaNguoiDung"]) != user_id:
        raise HTTPException(status_code=403, detail="Chỉ tác giả mới có quyền xóa bài viết của mình.")

    model.soft_delete_post(post_id)
    return {"ok": True, "message": f"Đã xóa bài viết #{post_id}."}


def list_post_comments(*, post_id: int, viewer_id: int) -> dict:
    _require_visible_post(post_id, viewer_id)
    blocked = model.get_blocked_user_ids(viewer_id)
    items = [c for c in model.list_comments(post_id) if int(c["MaNguoiDung"]) not in blocked]
    return {"items": items, "total": len(items)}


def add_comment(
    *,
    post_id: int,
    user_id: int,
    actor_name: str,
    noi_dung: str,
) -> dict:
    post = _require_visible_post(post_id, user_id)
    text = noi_dung.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Nội dung bình luận không được để trống.")
    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="Bình luận tối đa 2000 ký tự.")

    notif = None
    author_id = int(post["MaNguoiDung"])
    if author_id != user_id:
        notif = {
            "MaNguoiNhan": author_id,
            "MaNguoiThucHien": user_id,
            "LoaiThongBao": "BinhLuanBaiViet",
            "NoiDung": f"{actor_name} đã bình luận bài viết #{post_id}: {text[:80]}",
            "LienKet": f"/posts/{post_id}",
        }

    comment = model.create_comment_with_count(
        post_id=post_id,
        user_id=user_id,
        noi_dung=text,
        notification=notif,
    )
    _push_realtime_best_effort(notif)
    return {"ok": True, "message": "Đã đăng bình luận.", "comment": comment}


def delete_comment(*, post_id: int, comment_id: int, user_id: int) -> dict:
    post = model.get_post_by_id(post_id)
    if not post or post.get("TrangThai") != "HienThi":
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    comment = model.get_comment_by_id(comment_id)
    if not comment or int(comment["MaBaiViet"]) != post_id or comment.get("TrangThai") != "HienThi":
        raise HTTPException(status_code=404, detail="Không tìm thấy bình luận.")
    if int(comment["MaNguoiDung"]) != user_id and int(post["MaNguoiDung"]) != user_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa bình luận này.")

    model.soft_delete_comment_with_count(post_id, comment_id)
    return {"ok": True, "message": "Đã xóa bình luận."}


def toggle_like(*, post_id: int, user_id: int, actor_name: str) -> dict:
    post = _require_visible_post(post_id, user_id)
    author_id = int(post["MaNguoiDung"])
    notif = None
    if author_id != user_id:
        notif = {
            "MaNguoiNhan": author_id,
            "MaNguoiThucHien": user_id,
            "LoaiThongBao": "ThichBaiViet",
            "NoiDung": f"{actor_name} đã thích bài viết #{post_id} của bạn.",
            "LienKet": f"/posts/{post_id}",
        }

    result = model.toggle_post_like(post_id=post_id, user_id=user_id, notification=notif)
    if result.get("liked") and result.get("notification"):
        _push_realtime_best_effort(result["notification"])

    return {
        "ok": True,
        "liked": result["liked"],
        "so_luot_thich": result["so_luot_thich"],
        "message": "Đã thích bài viết." if result["liked"] else "Đã bỏ thích bài viết.",
    }


def _describe_relation(row: dict, viewer_id: int) -> str:
    if not row or not row.get("TrangThaiKetBan"):
        return "ChuaKetBan"
    status = row["TrangThaiKetBan"]
    if status == "BanBe":
        return "BanBe"
    if status == "ChoDuyet":
        return "ChoDuyet_Gui" if int(row["MaNguoiGui"]) == viewer_id else "ChoDuyet_Nhan"
    return status


def search_students(*, viewer_id: int, query: str = "", lop_id: int | None = None, limit: int = 30) -> dict:
    rows = model.search_students(viewer_id=viewer_id, query=query, lop_id=lop_id, limit=limit)
    items: list[dict] = []
    for row in rows:
        priv = _parse_privacy(row.get("CaiDatRiengTu"))
        is_friend = row.get("TrangThaiKetBan") == "BanBe"
        items.append(
            {
                "MaNguoiDung": row["MaNguoiDung"],
                "HoTen": row["HoTen"],
                "MaSinhVien": row.get("MaSinhVien"),
                "MaLop": row.get("MaLop"),
                "TenLop": row.get("TenLop"),
                "GioiThieu": row.get("GioiThieu"),
                "Email": _mask_contact_field(row.get("Email"), priv.get("hienEmail", "CongDong"), is_self=False, is_friend=is_friend),
                "SoDienThoai": _mask_contact_field(row.get("SoDienThoai"), priv.get("hienSdt", "BanBe"), is_self=False, is_friend=is_friend),
                "MaKetBan": row.get("MaKetBan"),
                "QuanHe": _describe_relation(row, viewer_id),
            }
        )
    return {"items": items, "total": len(items)}


def list_friends_and_requests(*, user_id: int) -> dict:
    rows = model.list_friend_relations(user_id)
    friends: list[dict] = []
    incoming: list[dict] = []
    outgoing: list[dict] = []

    for row in rows:
        priv = _parse_privacy(row.get("PeerRiengTu"))
        is_friend = row["TrangThai"] == "BanBe"
        entry = {
            "MaKetBan": row["MaKetBan"],
            "TrangThai": row["TrangThai"],
            "MaNguoiGui": row["MaNguoiGui"],
            "MaNguoiNhan": row["MaNguoiNhan"],
            "NgayTao": row.get("NgayTao"),
            "peer": {
                "MaNguoiDung": row["PeerId"],
                "HoTen": row["PeerHoTen"],
                "MaSinhVien": row.get("PeerMaSinhVien"),
                "MaLop": row.get("PeerMaLop"),
                "TenLop": row.get("PeerTenLop"),
                "Email": _mask_contact_field(row.get("PeerEmail"), priv.get("hienEmail", "CongDong"), is_self=False, is_friend=is_friend),
                "SoDienThoai": _mask_contact_field(row.get("PeerSoDienThoai"), priv.get("hienSdt", "BanBe"), is_self=False, is_friend=is_friend),
            },
        }
        if is_friend:
            friends.append(entry)
        elif int(row["MaNguoiNhan"]) == user_id:
            incoming.append(entry)
        else:
            outgoing.append(entry)

    return {
        "friends": friends,
        "incoming_requests": incoming,
        "outgoing_requests": outgoing,
    }


def send_friend_request(*, sender_id: int, sender_name: str, target_id: int) -> dict:
    if sender_id == target_id:
        raise HTTPException(status_code=400, detail="Không thể tự gửi lời mời kết bạn cho chính mình.")

    target = model.get_user_basic(target_id)
    if not target or target.get("TrangThai") != "HoatDong":
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên hợp lệ.")

    existing = model.get_relationship_between(sender_id, target_id)
    reuse_id: int | None = None
    if existing:
        st = existing["TrangThai"]
        if st == "DaChan":
            raise HTTPException(status_code=403, detail="Không thể gửi lời mời kết bạn do đang có trạng thái chặn.")
        if st == "BanBe":
            raise HTTPException(status_code=409, detail="Hai bạn đã là bạn bè.")
        if st == "ChoDuyet":
            if int(existing["MaNguoiGui"]) == sender_id:
                raise HTTPException(status_code=409, detail="Bạn đã gửi lời mời kết bạn cho người này trước đó.")
            raise HTTPException(
                status_code=409,
                detail=f"Người này đã gửi lời mời kết bạn cho bạn (Mã #{existing['MaKetBan']}); hãy chấp nhận trong mục Lời mời đến.",
            )
        reuse_id = int(existing["MaKetBan"])

    notif = {
        "MaNguoiNhan": target_id,
        "MaNguoiThucHien": sender_id,
        "LoaiThongBao": "LoiMoiKetBan",
        "NoiDung": f"{sender_name} đã gửi lời mời kết bạn cho bạn.",
        "LienKet": "/friends/requests",
    }
    try:
        friendship = model.upsert_friend_request(
            sender_id=sender_id,
            target_id=target_id,
            existing_id=reuse_id,
            notification=notif,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail="Lời mời kết bạn đã tồn tại.") from exc

    _push_realtime_best_effort(notif)
    return {"ok": True, "message": f"Đã gửi lời mời kết bạn tới {target['HoTen']}.", "friendship": friendship}


def respond_friend_request(
    *,
    friendship_id: int,
    user_id: int,
    responder_name: str,
    chap_nhan: bool,
) -> dict:
    existing = model.get_friendship_by_id(friendship_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Không tìm thấy lời mời kết bạn.")
    if int(existing["MaNguoiNhan"]) != user_id:
        raise HTTPException(status_code=403, detail="Chỉ người nhận lời mời mới được phép chấp nhận hoặc từ chối.")
    if existing["TrangThai"] != "ChoDuyet":
        raise HTTPException(status_code=409, detail="Lời mời kết bạn này không còn ở trạng thái chờ duyệt.")

    next_status = "BanBe" if chap_nhan else "TuChoi"
    notif = None
    if chap_nhan:
        notif = {
            "MaNguoiNhan": int(existing["MaNguoiGui"]),
            "MaNguoiThucHien": user_id,
            "LoaiThongBao": "ChapNhanKetBan",
            "NoiDung": f"{responder_name} đã chấp nhận lời mời kết bạn của bạn.",
            "LienKet": "/friends",
        }

    updated = model.update_friendship_status(
        friendship_id=friendship_id,
        trang_thai=next_status,
        notification=notif,
    )
    if chap_nhan:
        _push_realtime_best_effort(notif)

    msg = "Đã chấp nhận kết bạn." if chap_nhan else "Đã từ chối lời mời kết bạn."
    return {"ok": True, "message": msg, "friendship": updated}


def remove_friendship(*, friendship_id: int, user_id: int) -> dict:
    existing = model.get_friendship_by_id(friendship_id)
    if not existing or existing["TrangThai"] == "DaChan":
        raise HTTPException(status_code=404, detail="Không tìm thấy quan hệ kết bạn.")

    is_sender = int(existing["MaNguoiGui"]) == user_id
    is_receiver = int(existing["MaNguoiNhan"]) == user_id
    if not (is_sender or is_receiver):
        raise HTTPException(status_code=403, detail="Bạn không thuộc quan hệ kết bạn này.")
    if existing["TrangThai"] == "ChoDuyet" and not is_sender:
        raise HTTPException(status_code=403, detail="Người nhận vui lòng dùng nút Từ chối lời mời.")

    model.delete_friendship(friendship_id)
    msg = "Đã thu hồi lời mời kết bạn." if existing["TrangThai"] == "ChoDuyet" else "Đã hủy kết bạn."
    return {"ok": True, "message": msg}
