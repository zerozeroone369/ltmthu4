"""Tkinter Desktop View cho M2: Cây Cộng đồng 5 Cấp (Trường → Lớp) (Duy)."""
import tkinter as tk
from tkinter import ttk


class Module02View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M2 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M2: Cây Cộng đồng 5 Cấp (Trường → Lớp)", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Duy (Full-stack Module)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Quản lý trọn vẹn 5 cấp (Truong → Khoa → Nganh → KhoaHoc → Lop) trên 1 bảng CongDong tự tham chiếu MaCongDongCha; cấp API lọc nối tiếp cho màn Đăng ký & Hồ sơ; trang Admin sửa/ngừng đơn vị.", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: CongDong", font=("Consolas", 9)).pack(anchor="w")
