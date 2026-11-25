"""Tkinter Desktop View cho M3: Bài viết, Tương tác & Kết bạn (Duy)."""
import tkinter as tk
from tkinter import ttk


class Module03View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M3 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M3: Bài viết, Tương tác & Kết bạn", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Duy (Full-stack Module)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Đăng/Sửa/Xóa bài viết theo phạm vi CongDong (kèm đường dẫn TepDinhKem tùy chọn); Bình luận, Thích (chống trùng 1 lượt/người/bài); Tìm bạn học & Kết bạn 2 chiều (KetBan).", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: BaiViet, BinhLuan, TuongTac, KetBan", font=("Consolas", 9)).pack(anchor="w")
