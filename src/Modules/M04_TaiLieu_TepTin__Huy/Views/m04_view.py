"""Tkinter Desktop View cho M4: Tài liệu Học tập & Truyền tệp (Huy)."""
import tkinter as tk
from tkinter import ttk


class Module04View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M4 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M4: Tài liệu Học tập & Truyền tệp", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Huy (Full-stack Module)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Danh mục MonHoc; Tải lên tài liệu (<20MB PDF/DOCX/ảnh) lưu thông tin thẳng vào bảng TaiLieu; Tải tệp về máy và cộng SoLuotTai; Tìm kiếm theo môn & Chấm điểm 1–5★ (DanhGiaTaiLieu).", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: MonHoc, TaiLieu, DanhGiaTaiLieu", font=("Consolas", 9)).pack(anchor="w")
