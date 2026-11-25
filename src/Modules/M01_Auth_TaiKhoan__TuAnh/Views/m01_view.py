"""Tkinter Desktop View cho M1: Tài khoản, Hồ sơ & Quên mật khẩu (OTP) (Nguyễn Ngô Tú Anh)."""
import tkinter as tk
from tkinter import ttk


class Module01View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M1 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M1: Tài khoản, Hồ sơ & Quên mật khẩu (OTP)", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Nguyễn Ngô Tú Anh (Leader)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Đăng ký theo lớp (cấp MaLop trỏ cây CongDong), Đăng nhập JWT (theo VaiTro trong NguoiDung), Đăng xuất, Đổi mật khẩu, Quên MK qua MaOTP/HanOTP, Cập nhật hồ sơ & Đổi lớp.", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: NguoiDung", font=("Consolas", 9)).pack(anchor="w")
