"""End-to-end integration test across M01, M02, M03, M10 on server.app & client_app."""
from __future__ import annotations

import json
import tkinter as tk
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext

import client_app
import server
from src.Modules.M01_Auth_TaiKhoan__TuAnh.Models import m01_model
from src.Modules.M02_CongDong_5Cap__Duy.Models import m02_model
from src.Modules.M03_BaiViet_KetBan__Duy.Models import m03_model
from src.Modules.M10_QuanTri_KiemDuyet__TuAnh.Models import m10_model
from src.Shared.middlewares import auth_middleware

_PWD = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture()
def integrated_server_client(monkeypatch):
    communities = {
        1: {"MaCongDong": 1, "MaCongDongCha": None, "KyHieu": "CNTT-DEMO", "TenCongDong": "Đại học CNTT", "CapDo": "Truong", "NamBatDau": None, "TrangThai": "DangHoatDong"},
        2: {"MaCongDong": 2, "MaCongDongCha": 1, "KyHieu": "CNTT", "TenCongDong": "Khoa CNTT", "CapDo": "Khoa", "NamBatDau": None, "TrangThai": "DangHoatDong"},
        3: {"MaCongDong": 3, "MaCongDongCha": 2, "KyHieu": "MMT", "TenCongDong": "Ngành MMT", "CapDo": "Nganh", "NamBatDau": None, "TrangThai": "DangHoatDong"},
        4: {"MaCongDong": 4, "MaCongDongCha": 3, "KyHieu": "K2022", "TenCongDong": "Khóa 2022", "CapDo": "KhoaHoc", "NamBatDau": 2022, "TrangThai": "DangHoatDong"},
        5: {"MaCongDong": 5, "MaCongDongCha": 4, "KyHieu": "D22CQCN01", "TenCongDong": "Lớp D22CQCN01", "CapDo": "Lop", "NamBatDau": None, "TrangThai": "DangHoatDong"},
    }
    users = {
        1: {
            "MaNguoiDung": 1,
            "MaLop": 5,
            "VaiTro": "QuanTriVien",
            "MaSinhVien": "ADMIN01",
            "Email": "admin@dau.edu.vn",
            "MatKhauHash": _PWD.hash("Admin123!"),
            "HoTen": "Tú Anh Admin",
            "SoDienThoai": None,
            "AnhDaiDien": None,
            "GioiThieu": None,
            "CaiDatRiengTu": json.dumps({"hienSdt": "BanBe", "hienEmail": "CongDong", "hienBaiViet": "CongDong"}),
            "MaOTP": None,
            "HanOTP": None,
            "TrangThai": "HoatDong",
            "NgayTao": datetime.now(UTC).isoformat(),
            "NgayCapNhat": None,
        }
    }
    posts: dict[int, dict] = {}
    comments: dict[int, dict] = {}
    likes: set[tuple[int, int]] = set()
    friendships: dict[int, dict] = {}
    reports: dict[int, dict] = {}
    stored_notifs: list[dict] = []
    counters = {"c": 6, "u": 2, "p": 1, "cm": 1, "f": 1, "r": 1}

    def comm_children(parent_id=None, include_inactive=False):
        return sorted(
            [dict(c) for c in communities.values() if c["MaCongDongCha"] == parent_id and (include_inactive or c["TrangThai"] == "DangHoatDong")],
            key=lambda r: r["TenCongDong"],
        )

    def comm_chain(cid):
        chain, cur = [], communities.get(cid)
        while cur:
            chain.append(dict(cur))
            cur = communities.get(cur["MaCongDongCha"]) if cur["MaCongDongCha"] else None
        chain.reverse()
        return chain

    def create_comm(data):
        cid = counters["c"]
        counters["c"] += 1
        row = {"MaCongDong": cid, **data}
        communities[cid] = row
        return dict(row)

    def create_user(data):
        uid = counters["u"]
        counters["u"] += 1
        row = {
            "MaNguoiDung": uid,
            "MaLop": data.get("MaLop"),
            "VaiTro": data.get("VaiTro", "SinhVien"),
            "MaSinhVien": data.get("MaSinhVien"),
            "Email": data["Email"],
            "MatKhauHash": data["MatKhauHash"],
            "HoTen": data["HoTen"],
            "SoDienThoai": data.get("SoDienThoai"),
            "AnhDaiDien": None,
            "GioiThieu": data.get("GioiThieu"),
            "CaiDatRiengTu": json.dumps({"hienSdt": "BanBe", "hienEmail": "CongDong", "hienBaiViet": "CongDong"}),
            "MaOTP": None,
            "HanOTP": None,
            "TrangThai": "HoatDong",
            "NgayTao": datetime.now(UTC).isoformat(),
            "NgayCapNhat": None,
        }
        users[uid] = row
        return dict(row)

    def enrich_post(p):
        u, c = users[p["MaNguoiDung"]], communities[p["MaCongDong"]]
        return {**p, "TenTacGia": u["HoTen"], "TacGiaRiengTu": u["CaiDatRiengTu"], "TenCongDong": c["TenCongDong"], "CapDo": c["CapDo"]}

    def get_target(loai, tid):
        if loai == "BaiViet" and tid in posts:
            return {"id": tid, "owner_id": posts[tid]["MaNguoiDung"], "status": posts[tid]["TrangThai"], "preview": posts[tid]["NoiDung"]}
        return None

    def resolve_rep(*, report_id, admin_id, quyet_dinh, ghi_chu_xu_ly, report_status, content_status, lock_owner_id, notifications: list[dict]):
        rep = reports[report_id]
        if content_status and rep["LoaiNoiDung"] == "BaiViet":
            posts[rep["IdNoiDung"]]["TrangThai"] = content_status
        rep.update({"TrangThai": report_status, "QuyetDinh": quyet_dinh, "MaAdminXuLy": admin_id, "GhiChuXuLy": ghi_chu_xu_ly})
        stored_notifs.extend(notifications)
        return dict(rep)

    monkeypatch.setattr(auth_middleware, "get_jwt_secret", lambda: "integrated-secret-at-least-32-chars")
    monkeypatch.setattr(auth_middleware, "fetch_active_user_auth_state", lambda uid: users.get(uid))
    auth_middleware.clear_revoked_tokens()

    # Bind shared state to M01, M02, M03, M10 models
    monkeypatch.setattr(m01_model, "get_community_children", lambda parent_id=None: comm_children(parent_id))
    monkeypatch.setattr(m01_model, "get_active_class_by_id", lambda lid: communities.get(lid) if communities.get(lid, {}).get("CapDo") == "Lop" else None)
    monkeypatch.setattr(m01_model, "get_community_chain", comm_chain)
    monkeypatch.setattr(m01_model, "get_user_by_email", lambda em: next((dict(u) for u in users.values() if u["Email"] == em.lower()), None))
    monkeypatch.setattr(m01_model, "get_user_by_id", lambda uid: dict(users[uid]) if uid in users else None)
    monkeypatch.setattr(m01_model, "create_user", create_user)

    monkeypatch.setattr(m02_model, "get_community_by_id", lambda cid: dict(communities[cid]) if cid in communities else None)
    monkeypatch.setattr(m02_model, "get_community_children", comm_children)
    monkeypatch.setattr(m02_model, "get_community_chain", comm_chain)
    monkeypatch.setattr(m02_model, "find_duplicate_code", lambda *args, **kwargs: None)
    monkeypatch.setattr(m02_model, "create_community", create_comm)
    monkeypatch.setattr(m02_model, "list_communities", lambda **_kw: [dict(c) for c in communities.values()])

    def create_post_fn(*, user_id, cong_dong_id, danh_muc, noi_dung, tep_dinh_kem=None):
        pid = counters["p"]
        counters["p"] += 1
        posts[pid] = {
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
        return enrich_post(posts[pid])

    def upsert_friend_fn(*, sender_id, target_id, existing_id=None, notification=None):
        fid = counters["f"]
        counters["f"] += 1
        row = {"MaKetBan": fid, "MaNguoiGui": sender_id, "MaNguoiNhan": target_id, "TrangThai": "ChoDuyet"}
        friendships[fid] = row
        return dict(row)

    def update_friend_fn(*, friendship_id, trang_thai, notification=None):
        friendships[friendship_id]["TrangThai"] = trang_thai
        return dict(friendships[friendship_id])

    def create_report_fn(rep_id, loai, tid, ly_do, chi_tiet):
        rid = counters["r"]
        counters["r"] += 1
        row = {
            "MaBaoCao": rid,
            "MaNguoiBaoCao": rep_id,
            "LoaiNoiDung": loai,
            "IdNoiDung": tid,
            "LyDo": ly_do,
            "ChiTiet": chi_tiet,
            "TrangThai": "ChoDuyet",
            "QuyetDinh": None,
            "TenNguoiBaoCao": users[rep_id]["HoTen"],
        }
        reports[rid] = row
        return dict(row)

    monkeypatch.setattr(m03_model, "get_active_community_by_id", lambda cid: communities.get(cid))
    monkeypatch.setattr(m03_model, "get_user_basic", lambda uid: users.get(uid))
    monkeypatch.setattr(m03_model, "get_blocked_user_ids", lambda _uid: set())
    monkeypatch.setattr(m03_model, "get_friend_user_ids", lambda uid: {kb["MaNguoiNhan"] if kb["MaNguoiGui"] == uid else kb["MaNguoiGui"] for kb in friendships.values() if kb["TrangThai"] == "BanBe" and uid in (kb["MaNguoiGui"], kb["MaNguoiNhan"])})
    monkeypatch.setattr(m03_model, "get_relationship_between", lambda a, b: next((dict(kb) for kb in friendships.values() if {kb["MaNguoiGui"], kb["MaNguoiNhan"]} == {a, b}), None))
    monkeypatch.setattr(m03_model, "list_posts", lambda **_kw: [enrich_post(p) for p in posts.values() if p["TrangThai"] == "HienThi"])
    monkeypatch.setattr(m03_model, "get_post_by_id", lambda pid: enrich_post(posts[pid]) if pid in posts else None)
    monkeypatch.setattr(m03_model, "get_liked_post_ids", lambda uid, pids: {pid for pid in pids if (pid, uid) in likes})
    monkeypatch.setattr(m03_model, "create_post", create_post_fn)
    monkeypatch.setattr(m03_model, "upsert_friend_request", upsert_friend_fn)
    monkeypatch.setattr(m03_model, "get_friendship_by_id", lambda fid: dict(friendships[fid]) if fid in friendships else None)
    monkeypatch.setattr(m03_model, "update_friendship_status", update_friend_fn)

    monkeypatch.setattr(m10_model, "get_content_target", get_target)
    monkeypatch.setattr(m10_model, "create_report", create_report_fn)
    monkeypatch.setattr(m10_model, "get_report_by_id", lambda rid: dict(reports[rid]) if rid in reports else None)
    monkeypatch.setattr(m10_model, "resolve_report_transaction", resolve_rep)

    return TestClient(server.app), posts


def test_cross_module_m01_m02_m03_m10_workflow(integrated_server_client):
    client, posts = integrated_server_client

    # Health & M02/M03 status endpoints
    assert client.get("/health").status_code == 200
    assert client.get("/api/m02/status").json()["ok"] is True
    assert client.get("/api/m03/status").json()["ok"] is True

    # 1. Admin logs in (M01) and adds new Lop D22CQCN99 (M02)
    adm_tok = client.post("/api/m01/auth/login", json={"email": "admin@dau.edu.vn", "password": "Admin123!"}).json()["access_token"]
    adm_h = {"Authorization": f"Bearer {adm_tok}"}
    new_cls = client.post(
        "/api/m02/admin/communities",
        headers=adm_h,
        json={"cap_do": "Lop", "ma_cong_dong_cha": 4, "ky_hieu": "D22CQCN99", "ten_cong_dong": "Lớp D22CQCN99"},
    )
    assert new_cls.status_code == 201
    new_lop_id = new_cls.json()["community"]["MaCongDong"]

    # 2. Student A & B browse M02 children and register in M01 under new class
    children_k2022 = client.get("/api/m02/communities/4/children").json()["items"]
    assert any(c["MaCongDong"] == new_lop_id for c in children_k2022)

    reg_a = client.post("/api/m01/auth/register", json={"email": "sva@dau.edu.vn", "password": "Password1!", "ho_ten": "SV A", "ma_lop": new_lop_id})
    reg_b = client.post("/api/m01/auth/register", json={"email": "svb@dau.edu.vn", "password": "Password1!", "ho_ten": "SV B", "ma_lop": new_lop_id})
    assert reg_a.status_code == 201 and reg_b.status_code == 201
    assert reg_a.json()["user"]["community_chain"][-1]["KyHieu"] == "D22CQCN99"

    h_a = {"Authorization": f"Bearer {reg_a.json()['access_token']}"}
    h_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}
    uid_b = reg_b.json()["user"]["MaNguoiDung"]

    # 3. Student A sends friend request -> B accepts; Student A posts to class (M03)
    fr = client.post("/api/m03/friends/request", headers=h_a, json={"ma_nguoi_nhan": uid_b})
    assert fr.status_code == 201
    fid = fr.json()["friendship"]["MaKetBan"]
    assert client.put(f"/api/m03/friends/{fid}/respond", headers=h_b, json={"chap_nhan": True}).status_code == 200

    post_res = client.post("/api/m03/posts", headers=h_a, json={"cong_dong_id": new_lop_id, "noi_dung": "Bài test tích hợp liên module"})
    assert post_res.status_code == 201
    pid = post_res.json()["post"]["MaBaiViet"]

    # 4. Student B reports post (M10) -> Admin hides post (M10) -> disappears from M03
    rep = client.post("/api/m10/reports", headers=h_b, json={"loai_noi_dung": "BaiViet", "id_noi_dung": pid, "ly_do": "Kiểm thử kiểm duyệt"})
    assert rep.status_code == 201
    rid = rep.json()["report"]["MaBaoCao"]

    mod = client.put(f"/api/m10/admin/reports/{rid}", headers=adm_h, json={"quyet_dinh": "AnNoiDung"})
    assert mod.status_code == 200
    assert posts[pid]["TrangThai"] == "BiAn"
    assert client.get(f"/api/m03/posts/{pid}", headers=h_b).status_code == 404
    assert all(p["MaBaiViet"] != pid for p in client.get("/api/m03/posts", headers=h_b).json()["items"])


def test_desktop_client_app_smoke():
    try:
        app = client_app.MxhDesktopClient()
    except tk.TclError:
        pytest.skip("No GUI display available")
    app.withdraw()
    assert app.content is not None
    app.update_idletasks()
    app.destroy()
