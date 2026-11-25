"""TDD tests for M10: Admin User Management and Violation Moderation."""
from __future__ import annotations

import tkinter as tk
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.Modules.M10_QuanTri_KiemDuyet__TuAnh.Controllers.m10_controller import router
from src.Modules.M10_QuanTri_KiemDuyet__TuAnh.Models import m10_model
from src.Modules.M10_QuanTri_KiemDuyet__TuAnh.Views.m10_view import Module10View
from src.Shared.middlewares import auth_middleware


class FakeM10Repo:
    """In-memory repository simulating NguoiDung, BaoCaoViPham, BaiViet, and ThongBao."""

    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.users = {
            1: {"MaNguoiDung": 1, "MaLop": 5, "TenLop": "Lớp D22CQCN01", "VaiTro": "QuanTriVien", "MaSinhVien": "ADMIN01", "Email": "admin1@dau.edu.vn", "HoTen": "Admin Một", "TrangThai": "HoatDong", "NgayTao": now},
            2: {"MaNguoiDung": 2, "MaLop": 5, "TenLop": "Lớp D22CQCN01", "VaiTro": "SinhVien", "MaSinhVien": "SV001", "Email": "sv1@dau.edu.vn", "HoTen": "Sinh Viên Một", "TrangThai": "HoatDong", "NgayTao": now},
            3: {"MaNguoiDung": 3, "MaLop": 5, "TenLop": "Lớp D22CQCN01", "VaiTro": "SinhVien", "MaSinhVien": "SV002", "Email": "sv2@dau.edu.vn", "HoTen": "Sinh Viên Hai", "TrangThai": "HoatDong", "NgayTao": now},
        }
        self.posts = {
            10: {"id": 10, "owner_id": 2, "status": "HienThi", "preview": "Bài viết vi phạm nội quy"},
        }
        self.reports = {
            100: {
                "MaBaoCao": 100,
                "MaNguoiBaoCao": 3,
                "TenNguoiBaoCao": "Sinh Viên Hai",
                "MaAdminXuLy": None,
                "TenAdminXuLy": None,
                "LoaiNoiDung": "BaiViet",
                "IdNoiDung": 10,
                "LyDo": "Ngôn từ không phù hợp",
                "ChiTiet": "Spam trong lớp",
                "TrangThai": "ChoDuyet",
                "QuyetDinh": None,
                "GhiChuXuLy": None,
                "NgayGui": now,
                "NgayXuLy": None,
            }
        }
        self.notifications: list[dict] = []
        self.next_report_id = 101

    def list_users(self, search: str = "", vai_tro: str | None = None, trang_thai: str | None = None, limit: int = 50, offset: int = 0) -> dict:
        rows = list(self.users.values())
        if search:
            q = search.lower()
            rows = [r for r in rows if q in r["HoTen"].lower() or q in r["Email"].lower() or q in (r.get("MaSinhVien") or "").lower()]
        if vai_tro:
            rows = [r for r in rows if r["VaiTro"] == vai_tro]
        if trang_thai:
            rows = [r for r in rows if r["TrangThai"] == trang_thai]
        return {
            "items": [dict(r) for r in rows[offset : offset + limit]],
            "total": len(rows),
            "stats": {
                "total_users": len(self.users),
                "active_admins": self.count_active_admins(),
                "locked_users": sum(1 for u in self.users.values() if u["TrangThai"] != "HoatDong"),
            },
        }

    def get_user_by_id(self, user_id: int) -> dict | None:
        u = self.users.get(user_id)
        return dict(u) if u else None

    def count_active_admins(self) -> int:
        return sum(1 for u in self.users.values() if u["VaiTro"] == "QuanTriVien" and u["TrangThai"] == "HoatDong")

    def update_user_lock_status(self, user_id: int, trang_thai: str) -> dict | None:
        if user_id not in self.users:
            return None
        self.users[user_id]["TrangThai"] = trang_thai
        return dict(self.users[user_id])

    def update_user_role(self, user_id: int, vai_tro: str) -> dict | None:
        if user_id not in self.users:
            return None
        self.users[user_id]["VaiTro"] = vai_tro
        return dict(self.users[user_id])

    def get_content_target(self, loai_noi_dung: str, id_noi_dung: int) -> dict | None:
        if loai_noi_dung == "BaiViet":
            return dict(self.posts[id_noi_dung]) if id_noi_dung in self.posts else None
        if loai_noi_dung == "NguoiDung":
            u = self.users.get(id_noi_dung)
            return {"id": u["MaNguoiDung"], "owner_id": u["MaNguoiDung"], "status": u["TrangThai"], "preview": u["HoTen"]} if u else None
        return None

    def create_report(self, reporter_id: int, loai_noi_dung: str, id_noi_dung: int, ly_do: str, chi_tiet: str | None) -> dict:
        rid = self.next_report_id
        self.next_report_id += 1
        row = {
            "MaBaoCao": rid,
            "MaNguoiBaoCao": reporter_id,
            "TenNguoiBaoCao": self.users[reporter_id]["HoTen"],
            "MaAdminXuLy": None,
            "TenAdminXuLy": None,
            "LoaiNoiDung": loai_noi_dung,
            "IdNoiDung": id_noi_dung,
            "LyDo": ly_do,
            "ChiTiet": chi_tiet,
            "TrangThai": "ChoDuyet",
            "QuyetDinh": None,
            "GhiChuXuLy": None,
            "NgayGui": datetime.now(UTC),
            "NgayXuLy": None,
        }
        self.reports[rid] = row
        return dict(row)

    def list_reports(self, trang_thai: str | None = None, loai_noi_dung: str | None = None, limit: int = 50, offset: int = 0) -> dict:
        rows = list(self.reports.values())
        if trang_thai:
            rows = [r for r in rows if r["TrangThai"] == trang_thai]
        if loai_noi_dung:
            rows = [r for r in rows if r["LoaiNoiDung"] == loai_noi_dung]
        return {
            "items": [dict(r) for r in rows[offset : offset + limit]],
            "total": len(rows),
            "stats": {
                "cho_duyet": sum(1 for r in self.reports.values() if r["TrangThai"] == "ChoDuyet"),
                "da_xu_ly": sum(1 for r in self.reports.values() if r["TrangThai"] == "DaXuLy"),
                "tu_choi": sum(1 for r in self.reports.values() if r["TrangThai"] == "TuChoi"),
            },
        }

    def get_report_by_id(self, report_id: int) -> dict | None:
        r = self.reports.get(report_id)
        return dict(r) if r else None

    def resolve_report_transaction(
        self,
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
        r = self.reports[report_id]
        r["TrangThai"] = report_status
        r["QuyetDinh"] = quyet_dinh
        r["GhiChuXuLy"] = ghi_chu_xu_ly
        r["MaAdminXuLy"] = admin_id
        r["TenAdminXuLy"] = self.users[admin_id]["HoTen"]
        r["NgayXuLy"] = datetime.now(UTC)
        if content_status and r["LoaiNoiDung"] == "BaiViet" and r["IdNoiDung"] in self.posts:
            self.posts[r["IdNoiDung"]]["status"] = content_status
        if lock_owner_id and lock_owner_id in self.users:
            self.users[lock_owner_id]["TrangThai"] = "BiKhoa"
        self.notifications.extend(notifications)
        return dict(r)


@pytest.fixture()
def m10_env(monkeypatch):
    repo = FakeM10Repo()
    auth_middleware.clear_revoked_tokens()
    monkeypatch.setenv("JWT_SECRET", "unit-test-secret-key-at-least-32-chars")

    for name in (
        "list_users",
        "get_user_by_id",
        "count_active_admins",
        "update_user_lock_status",
        "update_user_role",
        "get_content_target",
        "create_report",
        "list_reports",
        "get_report_by_id",
        "resolve_report_transaction",
    ):
        monkeypatch.setattr(m10_model, name, getattr(repo, name))

    def _auth_state(user_id: int):
        u = repo.users.get(user_id)
        if not u:
            return None
        return {
            "MaNguoiDung": u["MaNguoiDung"],
            "TrangThai": u["TrangThai"],
            "VaiTro": u["VaiTro"],
            "Email": u["Email"],
            "HoTen": u["HoTen"],
            "MaLop": u["MaLop"],
        }

    monkeypatch.setattr(auth_middleware, "fetch_active_user_auth_state", _auth_state)

    app = FastAPI()
    app.include_router(router)
    admin_tok, _ = auth_middleware.create_access_token(1, "admin1@dau.edu.vn", "QuanTriVien")
    sv_tok, _ = auth_middleware.create_access_token(2, "sv1@dau.edu.vn", "SinhVien")
    return TestClient(app), repo, admin_tok, sv_tok


def test_non_admin_forbidden_on_admin_endpoints(m10_env):
    client, _, _, sv_tok = m10_env
    headers = {"Authorization": f"Bearer {sv_tok}"}
    assert client.get("/api/m10/admin/users", headers=headers).status_code == 403
    assert client.get("/api/m10/admin/reports", headers=headers).status_code == 403
    assert client.put("/api/m10/admin/users/3/lock", headers=headers, json={"trang_thai": "BiKhoa"}).status_code == 403


def test_last_active_admin_cannot_be_locked_or_demoted(m10_env):
    client, _, admin_tok, _ = m10_env
    headers = {"Authorization": f"Bearer {admin_tok}"}

    # Cannot lock self / last active admin
    lock_self = client.put("/api/m10/admin/users/1/lock", headers=headers, json={"trang_thai": "BiKhoa"})
    assert lock_self.status_code == 400

    # Cannot demote last active admin
    demote_last = client.put("/api/m10/admin/users/1/role", headers=headers, json={"vai_tro": "SinhVien"})
    assert demote_last.status_code == 400

    # Promote user 2 to QuanTriVien -> now there are 2 admins -> user 2 can be demoted or locked safely
    promote = client.put("/api/m10/admin/users/2/role", headers=headers, json={"vai_tro": "QuanTriVien"})
    assert promote.status_code == 200
    assert promote.json()["user"]["VaiTro"] == "QuanTriVien"

    lock_u2 = client.put("/api/m10/admin/users/2/lock", headers=headers, json={"trang_thai": "BiKhoa"})
    assert lock_u2.status_code == 200
    assert lock_u2.json()["user"]["TrangThai"] == "BiKhoa"

    # Unlock user 2
    unlock_u2 = client.put("/api/m10/admin/users/2/lock", headers=headers, json={"trang_thai": "HoatDong"})
    assert unlock_u2.status_code == 200
    assert unlock_u2.json()["user"]["TrangThai"] == "HoatDong"


def test_report_submission_and_moderation_decisions(m10_env):
    client, repo, admin_tok, sv_tok = m10_env
    admin_headers = {"Authorization": f"Bearer {admin_tok}"}
    sv_headers = {"Authorization": f"Bearer {sv_tok}"}

    # Report nonexistent target -> 404
    missing = client.post(
        "/api/m10/reports",
        headers=sv_headers,
        json={"loai_noi_dung": "BaiViet", "id_noi_dung": 9999, "ly_do": "Spam"},
    )
    assert missing.status_code == 404

    # Admin resolves existing report #100 by hiding post #10
    res = client.put(
        "/api/m10/admin/reports/100",
        headers=admin_headers,
        json={"quyet_dinh": "AnNoiDung", "ghi_chu_xu_ly": "Vi phạm quy định cộng đồng"},
    )
    assert res.status_code == 200, res.text
    report = res.json()["report"]
    assert report["TrangThai"] == "DaXuLy"
    assert report["QuyetDinh"] == "AnNoiDung"
    assert repo.posts[10]["status"] == "BiAn"
    assert len(repo.notifications) == 2

    # Double processing rejected
    again = client.put(
        "/api/m10/admin/reports/100",
        headers=admin_headers,
        json={"quyet_dinh": "BacBo"},
    )
    assert again.status_code == 409

    # New report targeting user 1 (last active admin) cannot trigger KhoaTaiKhoan
    rep_admin = client.post(
        "/api/m10/reports",
        headers=sv_headers,
        json={"loai_noi_dung": "NguoiDung", "id_noi_dung": 1, "ly_do": "Kiểm thử bảo vệ Admin cuối"},
    )
    assert rep_admin.status_code == 201
    rid = rep_admin.json()["report"]["MaBaoCao"]
    blocked = client.put(
        f"/api/m10/admin/reports/{rid}",
        headers=admin_headers,
        json={"quyet_dinh": "KhoaTaiKhoan"},
    )
    assert blocked.status_code == 400


def test_module10_tkinter_view_smoke():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No GUI display available")
    root.withdraw()
    view = Module10View(root, server_url="http://127.0.0.1:8000")
    assert len(view.nb.tabs()) == 4
    root.destroy()
