"""Tkinter Desktop View cho M7: Campus (Tin tức, Học bổng, Sự kiện) (Bảo)."""
import tkinter as tk
from tkinter import ttk


class Module07View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M7 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M7: Campus (Tin tức, Học bổng, Sự kiện)", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Bảo (Full-stack Module)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Sinh viên xem & lọc tin nhà trường (SuKien, HocBong, ThucTap, CLB, ThongBao) theo CongDong; Admin đăng mới, chỉnh sửa, ẩn/xóa tin Campus và phát thông báo tới sinh viên.", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: TinTruong", font=("Consolas", 9)).pack(anchor="w")
