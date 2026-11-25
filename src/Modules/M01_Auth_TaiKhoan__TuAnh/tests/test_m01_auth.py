"""TDD tests for M01: Auth, JWT, Profile, Privacy, and Forgot Password OTP."""
from __future__ import annotations

import tkinter as tk
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.Modules.M01_Auth_TaiKhoan__TuAnh.Controllers.m01_controller import router
from src.Modules.M01_Auth_TaiKhoan__TuAnh.Models import m01_model
from src.Modules.M01_Auth_TaiKhoan__TuAnh.Views.m01_view import Module01View
from src.Shared.middlewares import auth_middleware


class FakeM01Repo:
    """In-memory repository simulating PostgreSQL tables CongDong and NguoiDung."""

    def __init__(self) -> None:
        self.communities = {
            1: {"MaCongDong": 1, "MaCongDongCha": None, "KyHieu": "CNTT-DEMO", "TenCongDong": "Đại học CNTT", "CapDo": "Truong", "TrangThai": "DangHoatDong"},
            2: {"MaCongDong": 2, "MaCongDongCha": 1, "KyHieu": "CNTT", "TenCongDong": "Khoa CNTT", "CapDo": "Khoa", "TrangThai": "DangHoatDong"},
            3: {"MaCongDong": 3, "MaCongDongCha": 2, "KyHieu": "MMT", "TenCongDong": "Ngành MMT", "CapDo": "Nganh", "TrangThai": "DangHoatDong"},
            4: {"MaCongDong": 4, "MaCongDongCha": 3, "KyHieu": "K2022", "TenCongDong": "Khóa 2022", "CapDo": "KhoaHoc", "TrangThai": "DangHoatDong"},
            5: {"MaCongDong": 5, "MaCongDongCha": 4, "KyHieu": "D22CQCN01", "TenCongDong": "Lớp D22CQCN01", "CapDo": "Lop", "TrangThai": "DangHoatDong"},
            6: {"MaCongDong": 6, "MaCongDongCha": 4, "KyHieu": "D22CQCN02", "TenCongDong": "Lớp D22CQCN02", "CapDo": "Lop", "TrangThai": "DangHoatDong"},
        }
        self.users: dict[int, dict] = {}
        self.next_id = 1

    def get_community_children(self, parent_id: int | None = None) -> list[dict]:
        return [
            dict(c)
            for c in self.communities.values()
            if c["MaCongDongCha"] == parent_id and c["TrangThai"] == "DangHoatDong"
        ]

    def get_active_class_by_id(self, lop_id: int) -> dict | None:
        c = self.communities.get(lop_id)
        if c and c["CapDo"] == "Lop" and c["TrangThai"] == "DangHoatDong":
            return dict(c)
        return None

    def get_community_chain(self, lop_id: int) -> list[dict]:
        chain = []
        cur = self.communities.get(lop_id)
        while cur:
            chain.append(dict(cur))
            cur = self.communities.get(cur["MaCongDongCha"]) if cur["MaCongDongCha"] else None
        chain.reverse()
        return chain

    def get_user_by_email(self, email: str) -> dict | None:
        norm = email.strip().lower()
        for u in self.users.values():
            if u["Email"] == norm:
                return dict(u)
        return None

    def get_user_by_id(self, user_id: int) -> dict | None:
        u = self.users.get(user_id)
        return dict(u) if u else None

    def create_user(self, data: dict) -> dict:
        for u in self.users.values():
            if u["Email"] == data["Email"]:
                raise ValueError("DUPLICATE_EMAIL")
            if data.get("MaSinhVien") and u.get("MaSinhVien") == data["MaSinhVien"]:
                raise ValueError("DUPLICATE_MSSV")
        uid = self.next_id
        self.next_id += 1
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
            "CaiDatRiengTu": '{"hienSdt":"BanBe","hienEmail":"CongDong"}',
            "MaOTP": None,
            "HanOTP": None,
            "TrangThai": "HoatDong",
            "NgayTao": datetime.now(UTC),
            "NgayCapNhat": None,
        }
        self.users[uid] = row
        return dict(row)

    def update_password_hash(self, user_id: int, password_hash: str) -> bool:
        if user_id not in self.users:
            return False
        self.users[user_id]["MatKhauHash"] = password_hash
        self.users[user_id]["NgayCapNhat"] = datetime.now(UTC)
        return True

    def save_otp(self, user_id: int, otp_code: str, expires_minutes: int = 10) -> dict | None:
        if user_id not in self.users:
            return None
        exp = datetime.now(UTC) + timedelta(minutes=expires_minutes)
        self.users[user_id]["MaOTP"] = otp_code
        self.users[user_id]["HanOTP"] = exp
        self.users[user_id]["NgayCapNhat"] = datetime.now(UTC)
        return dict(self.users[user_id])

    def reset_password_with_otp(self, user_id: int, new_password_hash: str) -> bool:
        if user_id not in self.users:
            return False
        self.users[user_id]["MatKhauHash"] = new_password_hash
        self.users[user_id]["MaOTP"] = None
        self.users[user_id]["HanOTP"] = None
        self.users[user_id]["NgayCapNhat"] = datetime.now(UTC)
        return True

    def update_user_profile(self, user_id: int, fields: dict) -> dict | None:
        if user_id not in self.users:
            return None
        if fields.get("MaSinhVien"):
            for uid, u in self.users.items():
                if uid != user_id and u.get("MaSinhVien") == fields["MaSinhVien"]:
                    raise ValueError("DUPLICATE_MSSV")
        self.users[user_id].update(fields)
        self.users[user_id]["NgayCapNhat"] = datetime.now(UTC)
        return dict(self.users[user_id])


@pytest.fixture()
def m01_env(monkeypatch):
    repo = FakeM01Repo()
    auth_middleware.clear_revoked_tokens()
    monkeypatch.setenv("JWT_SECRET", "unit-test-secret-key-at-least-32-chars")
    monkeypatch.setattr(m01_model, "get_community_children", repo.get_community_children)
    monkeypatch.setattr(m01_model, "get_active_class_by_id", repo.get_active_class_by_id)
    monkeypatch.setattr(m01_model, "get_community_chain", repo.get_community_chain)
    monkeypatch.setattr(m01_model, "get_user_by_email", repo.get_user_by_email)
    monkeypatch.setattr(m01_model, "get_user_by_id", repo.get_user_by_id)
    monkeypatch.setattr(m01_model, "create_user", repo.create_user)
    monkeypatch.setattr(m01_model, "update_password_hash", repo.update_password_hash)
    monkeypatch.setattr(m01_model, "save_otp", repo.save_otp)
    monkeypatch.setattr(m01_model, "reset_password_with_otp", repo.reset_password_with_otp)
    monkeypatch.setattr(m01_model, "update_user_profile", repo.update_user_profile)

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
    return TestClient(app), repo


def test_register_forces_student_role_hashes_password_and_validates_class(m01_env):
    client, repo = m01_env
    # Non-Lop node (Truong id=1) must be rejected
    bad = client.post(
        "/api/m01/auth/register",
        json={
            "email": "Student@DAU.EDU.VN",
            "password": "Password123!",
            "ho_ten": "Sinh Viên Test",
            "ma_lop": 1,
            "vai_tro": "QuanTriVien",
        },
    )
    assert bad.status_code == 400

    res = client.post(
        "/api/m01/auth/register",
        json={
            "email": "Student@DAU.EDU.VN",
            "password": "Password123!",
            "ho_ten": "Sinh Viên Test",
            "ma_sinh_vien": "2351220001",
            "ma_lop": 5,
            "vai_tro": "QuanTriVien",
        },
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["access_token"]
    assert data["user"]["Email"] == "student@dau.edu.vn"
    assert data["user"]["VaiTro"] == "SinhVien"
    assert "MatKhauHash" not in data["user"]
    assert len(data["user"]["community_chain"]) == 5

    stored = repo.get_user_by_email("student@dau.edu.vn")
    assert stored["MatKhauHash"] != "Password123!"
    assert stored["MatKhauHash"].startswith("$2")

    dup = client.post(
        "/api/m01/auth/register",
        json={
            "email": "student@dau.edu.vn",
            "password": "Password123!",
            "ho_ten": "Trùng Email",
            "ma_lop": 5,
        },
    )
    assert dup.status_code == 409


def test_login_logout_jwt_and_locked_account_blocked(m01_env):
    client, repo = m01_env
    client.post(
        "/api/m01/auth/register",
        json={
            "email": "user1@dau.edu.vn",
            "password": "Secret123!",
            "ho_ten": "User One",
            "ma_lop": 5,
        },
    )

    wrong = client.post("/api/m01/auth/login", json={"email": "user1@dau.edu.vn", "password": "WrongPassword"})
    assert wrong.status_code == 401

    ok = client.post("/api/m01/auth/login", json={"email": "user1@dau.edu.vn", "password": "Secret123!"})
    assert ok.status_code == 200
    token = ok.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/m01/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["user"]["Email"] == "user1@dau.edu.vn"

    # Logout must revoke current token immediately
    out = client.post("/api/m01/auth/logout", headers=headers)
    assert out.status_code == 200
    assert client.get("/api/m01/users/me", headers=headers).status_code == 401

    # Login again then lock user -> token and new login must be rejected
    ok2 = client.post("/api/m01/auth/login", json={"email": "user1@dau.edu.vn", "password": "Secret123!"})
    token2 = ok2.json()["access_token"]
    repo.users[1]["TrangThai"] = "BiKhoa"
    assert client.get("/api/m01/users/me", headers={"Authorization": f"Bearer {token2}"}).status_code == 401
    assert client.post("/api/m01/auth/login", json={"email": "user1@dau.edu.vn", "password": "Secret123!"}).status_code == 403


def test_change_password_and_forgot_otp_reset_flow(m01_env):
    client, repo = m01_env
    reg = client.post(
        "/api/m01/auth/register",
        json={"email": "otp@dau.edu.vn", "password": "OldPassword1!", "ho_ten": "OTP Student", "ma_lop": 5},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    bad_pw = client.put(
        "/api/m01/users/password",
        headers=headers,
        json={"old_password": "WrongOldPassword", "new_password": "NewPassword2!"},
    )
    assert bad_pw.status_code == 400

    ok_pw = client.put(
        "/api/m01/users/password",
        headers=headers,
        json={"old_password": "OldPassword1!", "new_password": "NewPassword2!"},
    )
    assert ok_pw.status_code == 200

    otp_res = client.post("/api/m01/auth/forgot-otp", json={"email": "otp@dau.edu.vn"})
    assert otp_res.status_code == 200
    otp_code = otp_res.json().get("demo_otp")
    assert otp_code and len(otp_code) == 6

    wrong_otp = client.post(
        "/api/m01/auth/reset-pw",
        json={"email": "otp@dau.edu.vn", "otp": "000000" if otp_code != "000000" else "999999", "new_password": "ResetPass3!"},
    )
    assert wrong_otp.status_code == 400

    # Expired OTP rejected
    repo.users[1]["HanOTP"] = datetime.now(UTC) - timedelta(minutes=1)
    expired_res = client.post(
        "/api/m01/auth/reset-pw",
        json={"email": "otp@dau.edu.vn", "otp": otp_code, "new_password": "ResetPass3!"},
    )
    assert expired_res.status_code == 400

    # Valid OTP resets password and clears OTP fields
    repo.users[1]["HanOTP"] = datetime.now(UTC) + timedelta(minutes=5)
    reset_ok = client.post(
        "/api/m01/auth/reset-pw",
        json={"email": "otp@dau.edu.vn", "otp": otp_code, "new_password": "ResetPass3!"},
    )
    assert reset_ok.status_code == 200
    assert repo.users[1]["MaOTP"] is None
    assert repo.users[1]["HanOTP"] is None

    login_new = client.post("/api/m01/auth/login", json={"email": "otp@dau.edu.vn", "password": "ResetPass3!"})
    assert login_new.status_code == 200


def test_update_profile_class_and_privacy_preferences(m01_env):
    client, _ = m01_env
    reg = client.post(
        "/api/m01/auth/register",
        json={"email": "prof@dau.edu.vn", "password": "Password123!", "ho_ten": "Profile User", "ma_lop": 5},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    bad_priv = client.put(
        "/api/m01/users/profile",
        headers=headers,
        json={"cai_dat_rieng_tu": {"hienSdt": "KhongHopLe"}},
    )
    assert bad_priv.status_code == 400

    upd = client.put(
        "/api/m01/users/profile",
        headers=headers,
        json={
            "ho_ten": "Profile Updated",
            "so_dien_thoai": "0901234567",
            "gioi_thieu": "Sinh viên MMT",
            "ma_lop": 6,
            "cai_dat_rieng_tu": {"hienSdt": "ChiMinhToi", "hienEmail": "BanBe"},
        },
    )
    assert upd.status_code == 200
    user = upd.json()["user"]
    assert user["HoTen"] == "Profile Updated"
    assert user["MaLop"] == 6
    assert user["CaiDatRiengTu"]["hienSdt"] == "ChiMinhToi"
    assert user["CaiDatRiengTu"]["hienEmail"] == "BanBe"


def test_module01_tkinter_view_smoke():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No GUI display available")
    root.withdraw()
    view = Module01View(root, server_url="http://127.0.0.1:8000")
    assert len(view.notebook.tabs()) == 6
    root.destroy()
