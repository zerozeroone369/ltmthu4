"""Tkinter Desktop View cho M6: Nhóm học Tập (Study Groups) (Bảo)."""
import tkinter as tk
from tkinter import ttk


class Module06View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M6 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M6: Nhóm học Tập (Study Groups)", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Bảo (Full-stack Module)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Sinh viên tạo nhóm học (thành Trưởng nhóm); Tìm & Gửi đơn xin gia nhập (lưu ngay vào ThanhVienNhom trạng thái 'ChoDuyet'); Trưởng nhóm duyệt/từ chối theo sĩ số tối đa; Đổi sức chứa & Bàn giao trưởng nhóm khi rời.", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: NhomHoc, ThanhVienNhom", font=("Consolas", 9)).pack(anchor="w")
