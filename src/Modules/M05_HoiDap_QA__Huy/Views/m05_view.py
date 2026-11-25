"""Tkinter Desktop View cho M5: Hỏi đáp Học thuật (Q&A & Upvote) (Huy)."""
import tkinter as tk
from tkinter import ttk


class Module05View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M5 — kết nối Render Server."""

    def __init__(self, parent, server_url: str = ""):
        super().__init__(parent, padding=16)
        self.server_url = server_url
        ttk.Label(self, text="M5: Hỏi đáp Học thuật (Q&A & Upvote)", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(self, text="Phụ trách: Huy (Full-stack Module)", foreground="#2563eb").pack(anchor="w", pady=(2, 8))
        ttk.Label(self, text="Chức năng: Đặt câu hỏi theo MonHoc kèm từ khóa TheTuKhoa (#Socket, #SQL, #Python); Gửi câu trả lời; Bấm Upvote hữu ích (1 lần/người qua BinhChonCauTraLoi); Chủ câu hỏi chốt Đáp án đúng.", wraplength=640, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Bảng PostgreSQL: CauHoi, CauTraLoi, BinhChonCauTraLoi", font=("Consolas", 9)).pack(anchor="w")
