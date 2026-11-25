"""Tkinter Desktop View cho M10: Quản trị Hệ thống & Kiểm duyệt (Admin) (Nguyễn Ngô Tú Anh)."""
import tkinter as tk
from tkinter import ttk


class Module10View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M10 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M10: Quản trị Hệ thống & Kiểm duyệt (Admin)", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Nguyễn Ngô Tú Anh (Leader)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Quản lý danh sách tài khoản (đổi vai trò, khóa/mở khóa chống khóa Admin cuối cùng); Kiểm duyệt đơn BaoCaoViPham (bác bỏ, ẩn, xóa mềm nội dung vi phạm hoặc khóa tài khoản, lưu thẳng kết quả xử lý trên BaoCaoViPham); nhúng View của M02 & M07.", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: BaoCaoViPham, NguoiDung", font=("Consolas", 9)).pack(anchor="w")
