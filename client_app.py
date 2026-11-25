"""
App Desktop Client (Python Tkinter — KHÔNG phải trang Web)
Chạy trực tiếp trên máy tính sinh viên/giảng viên để kết nối tới Python Server trên Render.
"""
import json
import os
import tkinter as tk
from tkinter import ttk
import urllib.request

from dotenv import load_dotenv
from src.Modules.M01_Auth_TaiKhoan__TuAnh.Views.m01_view import Module01View

load_dotenv()
DEFAULT_SERVER = os.getenv("SERVER_URL", "http://127.0.0.1:8000")


class MxhDesktopClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mạng Xã Hội Sinh Viên — Python Desktop Client (MVC)")
        self.geometry("920x600")

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Server Cloud URL:").pack(side="left")
        self.url_var = tk.StringVar(value=DEFAULT_SERVER)
        ttk.Entry(top, textvariable=self.url_var, width=48).pack(side="left", padx=6)
        ttk.Button(top, text="Kiểm tra kết nối Server", command=self.check_server).pack(side="left")
        self.status_lbl = ttk.Label(top, text="Chưa kiểm tra", foreground="#64748b")
        self.status_lbl.pack(side="left", padx=10)

        ttk.Separator(self, orient="horizontal").pack(fill="x")
        self.content = Module01View(self, server_url=DEFAULT_SERVER)
        self.content.pack(fill="both", expand=True)

    def check_server(self):
        url = self.url_var.get().rstrip("/") + "/health"
        try:
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.status_lbl.config(text=f"Kết nối OK ({data.get('database')})", foreground="#15803d")
        except Exception as exc:
            self.status_lbl.config(text=f"Lỗi: {exc}", foreground="#dc2626")


if __name__ == "__main__":
    app = MxhDesktopClient()
    app.mainloop()
