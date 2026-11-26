"""Unit & API tests cho M03: Bài viết, Bình luận, Thích (TuongTac) & Kết bạn (KetBan)."""
from __future__ import annotations

import json
import tkinter as tk
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.Modules.M03_BaiViet_KetBan__Duy.Controllers.m03_controller import router
from src.Modules.M03_BaiViet_KetBan__Duy.Models import m03_model
from src.Modules.M03_BaiViet_KetBan__Duy.Views.m03_view import Module03View
from src.Shared.middlewares import auth_middleware


class FakeM03Repo:
    """In-memory repository simulating BaiViet, BinhLuan, TuongTac, KetBan, ThongBao."""

    def __init__(self) -> None:
        self.communities = {
            1: {"MaCongDong": 1, "MaCongDongCha": None, "KyHieu": "CNTT-DEMO", "TenCongDong": "Đại học CNTT", "CapDo": "Truong", "TrangThai": "DangHoatDong"},
            5: {"MaCongDong": 5, "MaCongDongCha": 4, "KyHieu": "D22CQCN01", "TenCongDong": "Lớp D22CQCN01", "CapDo": "Lop", "TrangThai": "DangHoatDong"},
        }
        self.users = {
            1: {"MaNguoiDung": 1, "MaLop": 5, "VaiTro": "SinhVien", "MaSinhVien": "SV001", "Email": "duy@dau.edu.vn", "HoTen": "Nguyễn Duy", "SoDienThoai": "0901111111", "AnhDaiDien": None, "GioiThieu": "LTM", "CaiDatRiengTu": json.dumps({"hienSdt": "BanBe", "hienEmail": "CongDong", "hienBaiViet": "CongDong"}), "TrangThai": "HoatDong"},
            2: {"MaNguoiDung": 2, "MaLop": 5, "VaiTro": "SinhVien", "MaSinhVien": "SV002", "Email": "huy@dau.edu.vn", "HoTen": "Minh Huy", "SoDienThoai": "0902222222", "AnhDaiDien": None, "GioiThieu": "QA", "CaiDatRiengTu": json.dumps({"hienSdt": "ChiMinhToi", "hienEmail": "BanBe", "hienBaiViet": "BanBe"}), "TrangThai": "HoatDong"},
            3: {"MaNguoiDung": 3, "MaLop": 5, "VaiTro": "SinhVien", "MaSinhVien": "SV003", "Email": "bao@dau.edu.vn", "HoTen": "Gia Bảo", "SoDienThoai": "0903333333", "AnhDaiDien": None, "GioiThieu": "Campus", "CaiDatRiengTu": json.dumps({"hienSdt": "CongDong", "hienEmail": "ChiMinhToi", "hienBaiViet": "ChiMinhToi"}), "TrangThai": "HoatDong"},
        }
        self.posts: dict[int, dict] = {}
        self.comments: dict[int, dict] = {}
        self.likes: set[tuple[int, int]] = set()
        self.friendships: dict[int, dict] = {}
        self.notifications: list[dict] = []
        self.next_post_id = 1
        self.next_comment_id = 1
        self.next_friendship_id = 1

    def get_active_community_by_id(self, community_id: int) -> dict | None:
        c = self.communities.get(community_id)
        return dict(c) if c and c["TrangThai"] == "DangHoatDong" else None

    def get_user_basic(self, user_id: int) -> dict | None:
        u = self.users.get(user_id)
        return dict(u) if u else None

    def get_relationship_between(self, user_a: int, user_b: int) -> dict | None:
        for kb in self.friendships.values():
            if (kb["MaNguoiGui"] == user_a and kb["MaNguoiNhan"] == user_b) or (
                kb["MaNguoiGui"] == user_b and kb["MaNguoiNhan"] == user_a
            ):
                return dict(kb)
        return None

    def get_blocked_user_ids(self, user_id: int) -> set[int]:
        blocked = set()
        for kb in self.friendships.values():
            if kb["TrangThai"] == "DaChan" and user_id in (kb["MaNguoiGui"], kb["MaNguoiNhan"]):
                blocked.add(kb["MaNguoiNhan"] if kb["MaNguoiGui"] == user_id else kb["MaNguoiGui"])
        return blocked

    def get_friend_user_ids(self, user_id: int) -> set[int]:
        friends = set()
        for kb in self.friendships.values():
            if kb["TrangThai"] == "BanBe" and user_id in (kb["MaNguoiGui"], kb["MaNguoiNhan"]):
                friends.add(kb["MaNguoiNhan"] if kb["MaNguoiGui"] == user_id else kb["MaNguoiGui"])
        return friends

    def _enrich_post(self, p: dict) -> dict:
        u = self.users[p["MaNguoiDung"]]
        c = self.communities[p["MaCongDong"]]
        return {
            **p,
            "TenTacGia": u["HoTen"],
            "TacGiaRiengTu": u["CaiDatRiengTu"],
            "TenCongDong": c["TenCongDong"],
            "CapDo": c["CapDo"],
        }

    def list_posts(self, *, cong_dong_id=None, danh_muc=None, search="", limit=50, offset=0) -> list[dict]:
        rows = [p for p in self.posts.values() if p["TrangThai"] == "HienThi"]
        if cong_dong_id is not None:
            rows = [p for p in rows if p["MaCongDong"] == cong_dong_id]
        if danh_muc:
            rows = [p for p in rows if p["DanhMuc"] == danh_muc]
        if search.strip():
            q = search.strip().lower()
            rows = [p for p in rows if q in p["NoiDung"].lower() or q in self.users[p["MaNguoiDung"]]["HoTen"].lower()]
        rows.sort(key=lambda r: r["MaBaiViet"], reverse=True)
        return [self._enrich_post(p) for p in rows[offset : offset + limit]]

    def get_post_by_id(self, post_id: int) -> dict | None:
        p = self.posts.get(post_id)
        return self._enrich_post(p) if p else None

    def get_liked_post_ids(self, user_id: int, post_ids: list[int]) -> set[int]:
        return {pid for pid in post_ids if (pid, user_id) in self.likes}

    def create_post(self, *, user_id: int, cong_dong_id: int, danh_muc: str, noi_dung: str, tep_dinh_kem=None) -> dict:
        pid = self.next_post_id
        self.next_post_id += 1
        self.posts[pid] = {
            "MaBaiViet": pid,
            "MaNguoiDung": user_id,
            "MaCongDong": cong_dong_id,
            "DanhMuc": danh_muc,
            "NoiDung": noi_dung,
            "TepDinhKem": tep_dinh_kem,
            "SoLuotThich": 0,
            "SoBinhLuan": 0,
            "TrangThai": "HienThi",
            "NgayTao": datetime.now(UTC).isoformat(),
            "NgayCapNhat": None,
        }
        return self.get_post_by_id(pid)

    def update_post(self, post_id: int, fields: dict) -> dict | None:
        p = self.posts.get(post_id)
        if not p:
            return None
        p.update(fields)
        p["NgayCapNhat"] = datetime.now(UTC).isoformat()
        return self.get_post_by_id(post_id)

    def soft_delete_post(self, post_id: int) -> bool:
        p = self.posts.get(post_id)
        if not p or p["TrangThai"] != "HienThi":
            return False
        p["TrangThai"] = "DaXoa"
        return True

    def list_comments(self, post_id: int) -> list[dict]:
        rows = [
            {**c, "TenNguoiBinhLuan": self.users[c["MaNguoiDung"]]["HoTen"]}
            for c in self.comments.values()
            if c["MaBaiViet"] == post_id and c["TrangThai"] == "HienThi"
        ]
        return sorted(rows, key=lambda r: r["MaBinhLuan"])

    def get_comment_by_id(self, comment_id: int) -> dict | None:
        c = self.comments.get(comment_id)
        if not c:
            return None
        return {**c, "TenNguoiBinhLuan": self.users[c["MaNguoiDung"]]["HoTen"]}

    def create_comment_with_count(self, *, post_id: int, user_id: int, noi_dung: str, notification=None) -> dict:
        cid = self.next_comment_id
        self.next_comment_id += 1
        self.comments[cid] = {
            "MaBinhLuan": cid,
            "MaBaiViet": post_id,
            "MaNguoiDung": user_id,
            "NoiDung": noi_dung,
            "TrangThai": "HienThi",
            "NgayTao": datetime.now(UTC).isoformat(),
        }
        self.posts[post_id]["SoBinhLuan"] += 1
        if notification:
            self.notifications.append(dict(notification))
        return self.get_comment_by_id(cid)

    def soft_delete_comment_with_count(self, post_id: int, comment_id: int) -> bool:
        c = self.comments.get(comment_id)
        if not c or c["MaBaiViet"] != post_id or c["TrangThai"] != "HienThi":
            return False
        c["TrangThai"] = "DaXoa"
        self.posts[post_id]["SoBinhLuan"] = max(0, self.posts[post_id]["SoBinhLuan"] - 1)
        return True

    def toggle_post_like(self, *, post_id: int, user_id: int, notification=None) -> dict:
        key = (post_id, user_id)
        if key in self.likes:
            self.likes.remove(key)
            self.posts[post_id]["SoLuotThich"] = max(0, self.posts[post_id]["SoLuotThich"] - 1)
            return {"liked": False, "so_luot_thich": self.posts[post_id]["SoLuotThich"], "notification": None}
        self.likes.add(key)
        self.posts[post_id]["SoLuotThich"] += 1
        if notification:
            self.notifications.append(dict(notification))
        return {"liked": True, "so_luot_thich": self.posts[post_id]["SoLuotThich"], "notification": notification}

    def search_students(self, *, viewer_id: int, query: str = "", lop_id=None, limit: int = 30) -> list[dict]:
        rows = []
        q = query.strip().lower()
        for uid, u in self.users.items():
            if uid == viewer_id or u["TrangThai"] != "HoatDong":
                continue
            if lop_id is not None and u["MaLop"] != lop_id:
                continue
            if q and not (
                q in u["HoTen"].lower()
                or q in (u.get("MaSinhVien") or "").lower()
                or q in u["Email"].lower()
            ):
                continue
            rel = self.get_relationship_between(viewer_id, uid)
            if rel and rel["TrangThai"] == "DaChan":
                continue
            lop = self.communities.get(u["MaLop"])
            rows.append(
                {
                    **u,
                    "TenLop": lop["TenCongDong"] if lop else None,
                    "MaKetBan": rel["MaKetBan"] if rel else None,
                    "MaNguoiGui": rel["MaNguoiGui"] if rel else None,
                    "MaNguoiNhan": rel["MaNguoiNhan"] if rel else None,
                    "TrangThaiKetBan": rel["TrangThai"] if rel else None,
                }
            )
        return rows[:limit]

    def list_friend_relations(self, user_id: int) -> list[dict]:
        out = []
        for kb in self.friendships.values():
            if kb["TrangThai"] not in ("ChoDuyet", "BanBe"):
                continue
            if user_id not in (kb["MaNguoiGui"], kb["MaNguoiNhan"]):
                continue
            peer_id = kb["MaNguoiNhan"] if kb["MaNguoiGui"] == user_id else kb["MaNguoiGui"]
            peer = self.users[peer_id]
            lop = self.communities.get(peer["MaLop"])
            out.append(
                {
                    **kb,
                    "PeerId": peer["MaNguoiDung"],
                    "PeerHoTen": peer["HoTen"],
                    "PeerMaSinhVien": peer.get("MaSinhVien"),
                    "PeerEmail": peer["Email"],
                    "PeerSoDienThoai": peer.get("SoDienThoai"),
                    "PeerRiengTu": peer.get("CaiDatRiengTu"),
                    "PeerMaLop": peer.get("MaLop"),
                    "PeerTenLop": lop["TenCongDong"] if lop else None,
                }
            )
        return out

    def get_friendship_by_id(self, friendship_id: int) -> dict | None:
        kb = self.friendships.get(friendship_id)
        return dict(kb) if kb else None

    def upsert_friend_request(self, *, sender_id: int, target_id: int, existing_id=None, notification=None) -> dict:
        if existing_id is not None and existing_id in self.friendships:
            kb = self.friendships[existing_id]
            kb.update({"MaNguoiGui": sender_id, "MaNguoiNhan": target_id, "TrangThai": "ChoDuyet"})
        else:
            fid = self.next_friendship_id
            self.next_friendship_id += 1
            kb = {
                "MaKetBan": fid,
                "MaNguoiGui": sender_id,
                "MaNguoiNhan": target_id,
                "TrangThai": "ChoDuyet",
                "NgayTao": datetime.now(UTC).isoformat(),
                "NgayCapNhat": None,
            }
            self.friendships[fid] = kb
        if notification:
            self.notifications.append(dict(notification))
        return dict(kb)

    def update_friendship_status(self, *, friendship_id: int, trang_thai: str, notification=None) -> dict | None:
        kb = self.friendships.get(friendship_id)
        if not kb:
            return None
        kb["TrangThai"] = trang_thai
        kb["NgayCapNhat"] = datetime.now(UTC).isoformat()
        if notification:
            self.notifications.append(dict(notification))
        return dict(kb)

    def delete_friendship(self, friendship_id: int) -> bool:
        return self.friendships.pop(friendship_id, None) is not None


@pytest.fixture()
def m03_env(monkeypatch):
    repo = FakeM03Repo()
    monkeypatch.setattr(auth_middleware, "get_jwt_secret", lambda: "test-m03-secret-key-at-least-32b")
    monkeypatch.setattr(
        auth_middleware,
        "fetch_active_user_auth_state",
        lambda uid: repo.users.get(uid),
    )
    auth_middleware.clear_revoked_tokens()

    for attr in (
        "get_active_community_by_id",
        "get_user_basic",
        "get_relationship_between",
        "get_blocked_user_ids",
        "get_friend_user_ids",
        "list_posts",
        "get_post_by_id",
        "get_liked_post_ids",
        "create_post",
        "update_post",
        "soft_delete_post",
        "list_comments",
        "get_comment_by_id",
        "create_comment_with_count",
        "soft_delete_comment_with_count",
        "toggle_post_like",
        "search_students",
        "list_friend_relations",
        "get_friendship_by_id",
        "upsert_friend_request",
        "update_friendship_status",
        "delete_friendship",
    ):
        monkeypatch.setattr(m03_model, attr, getattr(repo, attr))

    app = FastAPI()
    app.include_router(router)
    tokens = {
        uid: auth_middleware.create_access_token(uid, repo.users[uid]["Email"], "SinhVien")[0]
        for uid in (1, 2, 3)
    }
    return TestClient(app), repo, tokens


def test_post_crud_author_ownership_likes_and_comments(m03_env):
    client, repo, tokens = m03_env
    h1 = {"Authorization": f"Bearer {tokens[1]}"}
    h2 = {"Authorization": f"Bearer {tokens[2]}"}

    # Author #1 creates a post
    created = client.post(
        "/api/m03/posts",
        headers=h1,
        json={"cong_dong_id": 5, "danh_muc": "HocTap", "noi_dung": "Ôn tập Socket TCP/UDP", "tep_dinh_kem": "uploads/note.pdf"},
    )
    assert created.status_code == 201, created.text
    post_id = created.json()["post"]["MaBaiViet"]

    # Non-author #2 cannot edit or delete post
    assert client.put(f"/api/m03/posts/{post_id}", headers=h2, json={"noi_dung": "Sửa trộm"}).status_code == 403
    assert client.delete(f"/api/m03/posts/{post_id}", headers=h2).status_code == 403

    # Author #1 edits post
    edited = client.put(f"/api/m03/posts/{post_id}", headers=h1, json={"noi_dung": "Ôn tập Socket & PostgreSQL"})
    assert edited.status_code == 200
    assert edited.json()["post"]["NoiDung"] == "Ôn tập Socket & PostgreSQL"

    # User #2 toggles Like on -> count=1, liked=True, notification stored
    like_on = client.post(f"/api/m03/posts/{post_id}/like", headers=h2)
    assert like_on.status_code == 200
    assert like_on.json()["liked"] is True
    assert like_on.json()["so_luot_thich"] == 1
    assert repo.notifications[-1]["LoaiThongBao"] == "ThichBaiViet"

    # User #2 toggles Like again -> no duplicate row, count=0, liked=False
    like_off = client.post(f"/api/m03/posts/{post_id}/like", headers=h2)
    assert like_off.json()["liked"] is False
    assert like_off.json()["so_luot_thich"] == 0

    # User #2 comments -> count incremented & notification added
    cmt = client.post(f"/api/m03/posts/{post_id}/comments", headers=h2, json={"noi_dung": "Bài hay quá!"})
    assert cmt.status_code == 201
    comment_id = cmt.json()["comment"]["MaBinhLuan"]
    assert repo.posts[post_id]["SoBinhLuan"] == 1
    assert repo.notifications[-1]["LoaiThongBao"] == "BinhLuanBaiViet"

    # Delete comment decrements SoBinhLuan
    del_cmt = client.delete(f"/api/m03/posts/{post_id}/comments/{comment_id}", headers=h2)
    assert del_cmt.status_code == 200
    assert repo.posts[post_id]["SoBinhLuan"] == 0

    # Author deletes post -> hidden from feed/detail
    assert client.delete(f"/api/m03/posts/{post_id}", headers=h1).status_code == 200
    assert client.get(f"/api/m03/posts/{post_id}", headers=h1).status_code == 404


def test_friends_two_way_privacy_and_block_visibility(m03_env):
    client, repo, tokens = m03_env
    h1 = {"Authorization": f"Bearer {tokens[1]}"}
    h2 = {"Authorization": f"Bearer {tokens[2]}"}
    h3 = {"Authorization": f"Bearer {tokens[3]}"}

    # User 3 has private post (ChiMinhToi); User 2 has friends-only post (BanBe)
    p2 = client.post("/api/m03/posts", headers=h2, json={"cong_dong_id": 5, "noi_dung": "Bài riêng bạn bè"}).json()["post"]["MaBaiViet"]
    p3 = client.post("/api/m03/posts", headers=h3, json={"cong_dong_id": 5, "noi_dung": "Nhật ký cá nhân"}).json()["post"]["MaBaiViet"]

    # Before friendship, User 1 sees neither p2 nor p3
    feed_before = [p["MaBaiViet"] for p in client.get("/api/m03/posts", headers=h1).json()["items"]]
    assert p2 not in feed_before and p3 not in feed_before

    # Search respects privacy masking before becoming friends (User 2 sets Email=BanBe, SDT=ChiMinhToi)
    search_before = client.get("/api/m03/friends/search?q=Huy", headers=h1).json()["items"]
    assert len(search_before) == 1
    assert search_before[0]["Email"] is None
    assert search_before[0]["SoDienThoai"] is None

    # User 1 cannot self-friend
    assert client.post("/api/m03/friends/request", headers=h1, json={"ma_nguoi_nhan": 1}).status_code == 400

    # User 1 sends friend request to User 2
    req = client.post("/api/m03/friends/request", headers=h1, json={"ma_nguoi_nhan": 2})
    assert req.status_code == 201
    fid = req.json()["friendship"]["MaKetBan"]

    # Duplicate request & reverse pending rejected
    assert client.post("/api/m03/friends/request", headers=h1, json={"ma_nguoi_nhan": 2}).status_code == 409
    assert client.post("/api/m03/friends/request", headers=h2, json={"ma_nguoi_nhan": 1}).status_code == 409

    # Sender #1 cannot accept own request -> 403
    assert client.put(f"/api/m03/friends/{fid}/respond", headers=h1, json={"chap_nhan": True}).status_code == 403

    # Recipient #2 accepts -> becomes bidirectional BanBe
    acc = client.put(f"/api/m03/friends/{fid}/respond", headers=h2, json={"chap_nhan": True})
    assert acc.status_code == 200
    assert acc.json()["friendship"]["TrangThai"] == "BanBe"

    # Now User 1 sees User 2's BanBe post & masked Email, while SDT (ChiMinhToi) remains hidden
    feed_after = [p["MaBaiViet"] for p in client.get("/api/m03/posts", headers=h1).json()["items"]]
    assert p2 in feed_after and p3 not in feed_after
    search_after = client.get("/api/m03/friends/search?q=Huy", headers=h1).json()["items"]
    assert search_after[0]["Email"] == "huy@dau.edu.vn"
    assert search_after[0]["SoDienThoai"] is None

    # Blocking (DaChan) hides user from search and posts immediately
    repo.friendships[fid]["TrangThai"] = "DaChan"
    assert client.get(f"/api/m03/posts/{p2}", headers=h1).status_code == 403
    assert client.get("/api/m03/friends/search?q=Huy", headers=h1).json()["items"] == []

    # Reject then resend friend request reuses row safely, then unfriend removes it
    req13 = client.post("/api/m03/friends/request", headers=h1, json={"ma_nguoi_nhan": 3})
    assert req13.status_code == 201
    fid13 = req13.json()["friendship"]["MaKetBan"]
    rej13 = client.put(f"/api/m03/friends/{fid13}/respond", headers=h3, json={"trang_thai": "TuChoi"})
    assert rej13.status_code == 200
    assert rej13.json()["friendship"]["TrangThai"] == "TuChoi"

    resend31 = client.post("/api/m03/friends/request", headers=h3, json={"ma_nguoi_nhan": 1})
    assert resend31.status_code == 201
    assert resend31.json()["friendship"]["MaKetBan"] == fid13
    assert resend31.json()["friendship"]["MaNguoiGui"] == 3
    assert client.put(f"/api/m03/friends/{fid13}/respond", headers=h1, json={"chap_nhan": True}).status_code == 200
    assert client.delete(f"/api/m03/friends/{fid13}", headers=h1).status_code == 200
    assert client.delete(f"/api/m03/friends/{fid13}", headers=h1).status_code == 404

    # Moderated hidden post (BiAn from M10) is excluded from feed & detail
    repo.posts[p2]["TrangThai"] = "BiAn"
    repo.friendships[fid]["TrangThai"] = "BanBe"
    assert client.get(f"/api/m03/posts/{p2}", headers=h1).status_code == 404


def test_module03_tkinter_view_smoke():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No GUI display available")
    root.withdraw()
    view = Module03View(root, server_url="http://127.0.0.1:8000")
    assert len(view.notebook.tabs()) == 2
    root.update_idletasks()
    root.destroy()
