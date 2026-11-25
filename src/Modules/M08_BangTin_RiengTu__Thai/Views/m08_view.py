"""Tkinter Desktop View cho M8: Khung Tkinter Chung, Bảng tin & Riêng tư (Thái)."""
import tkinter as tk
from tkinter import ttk


class Module08View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M8 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M8: Khung Tkinter Chung, Bảng tin & Riêng tư", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Thái (UI Lead)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Dựng khung cửa sổ Tkinter chính (Sidebar, Header, chuyển đổi 10 Module trong client_app.py) cho cả nhóm; Bảng tin thông minh lọc theo 5 cấp cộng đồng & 4 chủ đề; Quyền riêng tư (CaiDatRiengTu trong NguoiDung) & Chặn người dùng (KetBan DaChan).", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: NguoiDung, KetBan", font=("Consolas", 9)).pack(anchor="w")
