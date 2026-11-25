"""Tkinter Desktop View cho M9: Nhắn tin Realtime & Thông báo (Thái)."""
import tkinter as tk
from tkinter import ttk


class Module09View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M9 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M9: Nhắn tin Realtime & Thông báo", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Thái (UI Lead)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Mở kênh WebSocket /ws cho phép nhắn tin 1-1 và chat nhóm trực tiếp (lưu lịch sử TinNhan); Chuông thông báo & hộp thư ThongBao; cung cấp hàm send_notification() cho Duy, Huy, Bảo đẩy thông báo tức thì.", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: TinNhan, ThongBao", font=("Consolas", 9)).pack(anchor="w")
