"""Tkinter Desktop View cho M1: Tài khoản, Hồ sơ & Quên mật khẩu (OTP) (Nguyễn Ngô Tú Anh)."""
from __future__ import annotations

import threading
import tkinter as tk
import urllib.error
from tkinter import messagebox, ttk

from src.Modules.M10_QuanTri_KiemDuyet__TuAnh.Views.m10_view import Module10View

from .http_helper import http_json, run_async_tk

_COMMUNITY_LEVELS = [
    ("Truong", "Trường"),
    ("Khoa", "Khoa"),
    ("Nganh", "Ngành"),
    ("KhoaHoc", "Khóa"),
    ("Lop", "Lớp"),
]
_PRIVACY_OPTIONS = ["CongDong", "BanBe", "ChiMinhToi"]


class _CommunityCascadeSelector(ttk.Frame):
    """5-level cascading CongDong selector (Trường → Khoa → Ngành → Khóa → Lớp)."""

    def __init__(self, parent, get_server_url, on_error=None):
        super().__init__(parent)
        self._get_server_url = get_server_url
        self._on_error = on_error
        self._level_items: list[list[dict]] = [[] for _ in _COMMUNITY_LEVELS]
        self._vars: list[tk.StringVar] = []
        self._combos: list[ttk.Combobox] = []
        self._pending_chain_ids: list[int] = []

        for idx, (_, label) in enumerate(_COMMUNITY_LEVELS):
            row = idx // 2
            col = (idx % 2) * 2
            ttk.Label(self, text=f"{label}:").grid(row=row, column=col, sticky="w", padx=(0, 6), pady=3)
            var = tk.StringVar()
            combo = ttk.Combobox(self, textvariable=var, state="readonly", width=28)
            combo.grid(row=row, column=col + 1, sticky="ew", padx=(0, 14), pady=3)
            combo.bind("<<ComboboxSelected>>", lambda _e, level_idx=idx: self._on_select(level_idx))
            self._vars.append(var)
            self._combos.append(combo)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)

    def load_roots(self, preselect_chain_ids: list[int] | None = None) -> None:
        self._pending_chain_ids = list(preselect_chain_ids or [])
        self._fetch_children(0, None)

    def get_selected_lop_id(self) -> int | None:
        idx = len(_COMMUNITY_LEVELS) - 1
        sel = self._combos[idx].current()
        items = self._level_items[idx]
        if 0 <= sel < len(items):
            return int(items[sel]["MaCongDong"])
        return None

    def _on_select(self, level_idx: int) -> None:
        self._pending_chain_ids = []
        for downstream in range(level_idx + 1, len(_COMMUNITY_LEVELS)):
            self._level_items[downstream] = []
            self._vars[downstream].set("")
            self._combos[downstream]["values"] = []

        if level_idx + 1 >= len(_COMMUNITY_LEVELS):
            return
        sel = self._combos[level_idx].current()
        if sel < 0 or sel >= len(self._level_items[level_idx]):
            return
        parent_id = int(self._level_items[level_idx][sel]["MaCongDong"])
        self._fetch_children(level_idx + 1, parent_id)

    def _fetch_children(self, level_idx: int, parent_id: int | None) -> None:
        base = self._get_server_url()

        def worker():
            try:
                m02_url = (
                    f"{base}/api/m02/communities/roots"
                    if parent_id is None
                    else f"{base}/api/m02/communities/{parent_id}/children"
                )
                status, data = http_json(m02_url)
                if status == 404 or "items" not in data:
                    q = "" if parent_id is None else f"?parent_id={parent_id}"
                    status, data = http_json(f"{base}/api/m01/communities/children{q}")
                items = data.get("items", []) if status == 200 else []
                err_msg = None if status == 200 else data.get("detail", f"HTTP {status}")
            except (urllib.error.URLError, OSError, ValueError) as exc:
                items = []
                err_msg = str(exc)

            def apply():
                if not self.winfo_exists():
                    return
                if err_msg and self._on_error:
                    self._on_error(f"Không tải được danh sách cộng đồng: {err_msg}")
                self._apply_items(level_idx, items)

            self.after(0, apply)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_items(self, level_idx: int, items: list[dict]) -> None:
        self._level_items[level_idx] = items
        labels = [f"{it.get('TenCongDong', '')} ({it.get('KyHieu') or it['MaCongDong']})" for it in items]
        self._combos[level_idx]["values"] = labels
        if not items:
            self._vars[level_idx].set("")
            return

        chosen_idx = 0
        if level_idx < len(self._pending_chain_ids):
            target_id = self._pending_chain_ids[level_idx]
            for i, it in enumerate(items):
                if int(it["MaCongDong"]) == int(target_id):
                    chosen_idx = i
                    break

        self._combos[level_idx].current(chosen_idx)
        if level_idx + 1 < len(_COMMUNITY_LEVELS):
            next_parent = int(items[chosen_idx]["MaCongDong"])
            self._fetch_children(level_idx + 1, next_parent)


class Module01View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M1 — tích hợp M10 khi là Admin."""

    def __init__(self, parent, server_url: str = "http://127.0.0.1:8000", on_auth_success=None):
        super().__init__(parent, padding=12)
        self.server_url = server_url or "http://127.0.0.1:8000"
        self.on_auth_success = on_auth_success
        self.access_token: str = ""
        self.current_user: dict | None = None
        self._admin_view = None

        self._build_header()
        self._build_tabs()

    def get_server_url(self) -> str:
        master_var = getattr(self.master, "url_var", None)
        if master_var is not None:
            val = master_var.get().strip().rstrip("/")
            if val:
                return val
        return self.server_url.strip().rstrip("/")

    def get_token(self) -> str:
        return self.access_token

    def _set_status(self, message: str, is_error: bool = False) -> None:
        color = "#dc2626" if is_error else "#15803d"
        self.feedback_lbl.config(text=message, foreground=color)

    def _run_async(self, fn, on_done) -> None:
        run_async_tk(self, fn, on_done)

    def _build_header(self) -> None:
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", pady=(0, 8))

        title_box = ttk.Frame(hdr)
        title_box.pack(side="left", fill="x", expand=True)
        ttk.Label(
            title_box,
            text="M1: Tài khoản, Hồ sơ, Riêng tư & Quên mật khẩu (OTP)",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")
        self.session_lbl = ttk.Label(
            title_box,
            text="Trạng thái: Chưa đăng nhập",
            foreground="#475569",
        )
        self.session_lbl.pack(anchor="w")

        self.logout_btn = ttk.Button(hdr, text="Đăng xuất", command=self._handle_logout, state="disabled")
        self.logout_btn.pack(side="right")

        self.feedback_lbl = ttk.Label(self, text="", wraplength=860)
        self.feedback_lbl.pack(fill="x", pady=(0, 6))

    def _build_tabs(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.login_tab = ttk.Frame(self.notebook, padding=14)
        self.register_tab = ttk.Frame(self.notebook, padding=14)
        self.forgot_tab = ttk.Frame(self.notebook, padding=14)
        self.profile_tab = ttk.Frame(self.notebook, padding=14)
        self.password_tab = ttk.Frame(self.notebook, padding=14)
        self.admin_tab = ttk.Frame(self.notebook, padding=6)

        self.notebook.add(self.login_tab, text="Đăng nhập")
        self.notebook.add(self.register_tab, text="Đăng ký")
        self.notebook.add(self.forgot_tab, text="Quên mật khẩu (OTP)")
        self.notebook.add(self.profile_tab, text="Hồ sơ & Riêng tư")
        self.notebook.add(self.password_tab, text="Đổi mật khẩu")
        self.notebook.add(self.admin_tab, text="Quản trị Admin (M10)")

        self._build_login_tab()
        self._build_register_tab()
        self._build_forgot_tab()
        self._build_profile_tab()
        self._build_password_tab()
        self._build_admin_tab()
        self._refresh_session_ui()

    def _build_login_tab(self) -> None:
        box = ttk.LabelFrame(self.login_tab, text="Đăng nhập hệ thống", padding=14)
        box.pack(anchor="nw", fill="x")

        self.login_email = tk.StringVar()
        self.login_pw = tk.StringVar()
        self.login_show_pw = tk.BooleanVar(value=False)

        ttk.Label(box, text="Email sinh viên / Admin:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(box, textvariable=self.login_email, width=42).grid(row=0, column=1, sticky="w", padx=8, pady=5)

        ttk.Label(box, text="Mật khẩu:").grid(row=1, column=0, sticky="w", pady=5)
        self.login_pw_entry = ttk.Entry(box, textvariable=self.login_pw, width=42, show="*")
        self.login_pw_entry.grid(row=1, column=1, sticky="w", padx=8, pady=5)

        ttk.Checkbutton(
            box,
            text="Hiện mật khẩu",
            variable=self.login_show_pw,
            command=lambda: self.login_pw_entry.config(show="" if self.login_show_pw.get() else "*"),
        ).grid(row=1, column=2, sticky="w")

        ttk.Button(box, text="Đăng nhập", command=self._handle_login).grid(row=2, column=1, sticky="w", padx=8, pady=(10, 2))

    def _build_register_tab(self) -> None:
        box = ttk.LabelFrame(self.register_tab, text="Đăng ký tài khoản Sinh viên theo Lớp", padding=12)
        box.pack(fill="x", anchor="nw")

        self.reg_name = tk.StringVar()
        self.reg_email = tk.StringVar()
        self.reg_mssv = tk.StringVar()
        self.reg_phone = tk.StringVar()
        self.reg_pw = tk.StringVar()
        self.reg_pw2 = tk.StringVar()

        fields = [
            ("Họ và tên (*):", self.reg_name, False),
            ("Email (*):", self.reg_email, False),
            ("Mã sinh viên (MSSV):", self.reg_mssv, False),
            ("Số điện thoại:", self.reg_phone, False),
            ("Mật khẩu (*):", self.reg_pw, True),
            ("Xác nhận mật khẩu (*):", self.reg_pw2, True),
        ]
        for idx, (lbl, var, secret) in enumerate(fields):
            r = idx // 2
            c = (idx % 2) * 2
            ttk.Label(box, text=lbl).grid(row=r, column=c, sticky="w", pady=4)
            ttk.Entry(box, textvariable=var, width=28, show="*" if secret else "").grid(
                row=r, column=c + 1, sticky="ew", padx=(6, 16), pady=4
            )

        comm_frame = ttk.LabelFrame(self.register_tab, text="Chọn Cộng đồng 5 Cấp (Trường → Lớp)", padding=10)
        comm_frame.pack(fill="x", pady=(10, 6))
        self.reg_cascade = _CommunityCascadeSelector(
            comm_frame, self.get_server_url, on_error=lambda msg: self._set_status(msg, True)
        )
        self.reg_cascade.pack(fill="x")

        btns = ttk.Frame(self.register_tab)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Tải danh sách Trường/Lớp", command=lambda: self.reg_cascade.load_roots()).pack(side="left")
        ttk.Button(btns, text="Đăng ký tài khoản", command=self._handle_register).pack(side="left", padx=10)

        self.after(250, self.reg_cascade.load_roots)

    def _build_forgot_tab(self) -> None:
        step1 = ttk.LabelFrame(self.forgot_tab, text="Bước 1: Yêu cầu mã OTP 6 số", padding=12)
        step1.pack(fill="x", anchor="nw")
        self.fp_email = tk.StringVar()
        ttk.Label(step1, text="Email đã đăng ký:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(step1, textvariable=self.fp_email, width=40).grid(row=0, column=1, padx=8, pady=4)
        ttk.Button(step1, text="Gửi mã OTP", command=self._handle_request_otp).grid(row=0, column=2, padx=4)
        self.otp_hint_lbl = ttk.Label(step1, text="", foreground="#1d4ed8")
        self.otp_hint_lbl.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        step2 = ttk.LabelFrame(self.forgot_tab, text="Bước 2: Xác nhận OTP & Đặt mật khẩu mới", padding=12)
        step2.pack(fill="x", anchor="nw", pady=(12, 0))
        self.fp_otp = tk.StringVar()
        self.fp_new_pw = tk.StringVar()
        ttk.Label(step2, text="Mã OTP (6 số):").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(step2, textvariable=self.fp_otp, width=18).grid(row=0, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(step2, text="Mật khẩu mới:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(step2, textvariable=self.fp_new_pw, width=32, show="*").grid(row=1, column=1, sticky="w", padx=8, pady=4)
        ttk.Button(step2, text="Đặt lại mật khẩu", command=self._handle_reset_pw).grid(row=2, column=1, sticky="w", padx=8, pady=8)

    def _build_profile_tab(self) -> None:
        info = ttk.LabelFrame(self.profile_tab, text="Thông tin cá nhân & Đổi lớp", padding=12)
        info.pack(fill="x")

        self.prof_name = tk.StringVar()
        self.prof_mssv = tk.StringVar()
        self.prof_phone = tk.StringVar()
        self.prof_avatar = tk.StringVar()
        self.prof_bio = tk.StringVar()
        self.prof_chain_lbl = ttk.Label(info, text="Chuỗi cộng đồng: (Chưa gắn lớp)", foreground="#2563eb")
        self.prof_chain_lbl.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        rows = [
            ("Họ tên:", self.prof_name),
            ("Mã sinh viên:", self.prof_mssv),
            ("Số điện thoại:", self.prof_phone),
            ("URL Ảnh đại diện:", self.prof_avatar),
            ("Giới thiệu:", self.prof_bio),
        ]
        for idx, (lbl, var) in enumerate(rows, start=1):
            ttk.Label(info, text=lbl).grid(row=idx, column=0, sticky="w", pady=3)
            ttk.Entry(info, textvariable=var, width=48).grid(row=idx, column=1, sticky="ew", padx=8, pady=3)
        info.columnconfigure(1, weight=1)

        cls_frame = ttk.LabelFrame(self.profile_tab, text="Chuyển lớp sinh hoạt (5 cấp)", padding=10)
        cls_frame.pack(fill="x", pady=8)
        self.prof_cascade = _CommunityCascadeSelector(
            cls_frame, self.get_server_url, on_error=lambda msg: self._set_status(msg, True)
        )
        self.prof_cascade.pack(fill="x")

        priv = ttk.LabelFrame(self.profile_tab, text="Cài đặt Quyền riêng tư", padding=10)
        priv.pack(fill="x", pady=(0, 8))
        self.priv_sdt = tk.StringVar(value="BanBe")
        self.priv_email = tk.StringVar(value="CongDong")
        self.priv_post = tk.StringVar(value="CongDong")

        for col_idx, (lbl, var) in enumerate(
            [("Hiển thị SĐT:", self.priv_sdt), ("Hiển thị Email:", self.priv_email), ("Ai xem bài viết:", self.priv_post)]
        ):
            ttk.Label(priv, text=lbl).grid(row=0, column=col_idx * 2, sticky="w", padx=(0, 4))
            ttk.Combobox(priv, textvariable=var, values=_PRIVACY_OPTIONS, state="readonly", width=13).grid(
                row=0, column=col_idx * 2 + 1, sticky="w", padx=(0, 12)
            )

        action_bar = ttk.Frame(self.profile_tab)
        action_bar.pack(fill="x")
        ttk.Button(action_bar, text="Tải lại hồ sơ", command=self._handle_refresh_profile).pack(side="left")
        ttk.Button(action_bar, text="Lưu hồ sơ & Riêng tư", command=self._handle_save_profile).pack(side="left", padx=10)

    def _build_password_tab(self) -> None:
        box = ttk.LabelFrame(self.password_tab, text="Đổi mật khẩu tài khoản đang đăng nhập", padding=14)
        box.pack(anchor="nw", fill="x")
        self.cp_old = tk.StringVar()
        self.cp_new = tk.StringVar()
        self.cp_new2 = tk.StringVar()

        for idx, (lbl, var) in enumerate(
            [
                ("Mật khẩu hiện tại:", self.cp_old),
                ("Mật khẩu mới (>= 6 ký tự):", self.cp_new),
                ("Nhập lại mật khẩu mới:", self.cp_new2),
            ]
        ):
            ttk.Label(box, text=lbl).grid(row=idx, column=0, sticky="w", pady=5)
            ttk.Entry(box, textvariable=var, width=36, show="*").grid(row=idx, column=1, sticky="w", padx=8, pady=5)

        ttk.Button(box, text="Cập nhật mật khẩu", command=self._handle_change_password).grid(
            row=3, column=1, sticky="w", padx=8, pady=(8, 2)
        )

    def _build_admin_tab(self) -> None:
        try:
            self._admin_view = Module10View(
                self.admin_tab,
                server_url=self.get_server_url(),
                get_token=self.get_token,
                get_server_url=self.get_server_url,
            )
            self._admin_view.pack(fill="both", expand=True)
        except (tk.TclError, RuntimeError) as exc:
            ttk.Label(self.admin_tab, text=f"Không thể nạp giao diện Admin M10: {exc}", foreground="#dc2626").pack(
                anchor="w", padx=12, pady=12
            )

    def _refresh_session_ui(self) -> None:
        logged_in = bool(self.access_token and self.current_user)
        if logged_in and self.current_user:
            u = self.current_user
            role = u.get("VaiTro", "SinhVien")
            self.session_lbl.config(
                text=f"Đang đăng nhập: {u.get('HoTen')} ({u.get('Email')}) • Vai trò: {role}",
                foreground="#15803d",
            )
            self.logout_btn.config(state="normal")
            self.notebook.tab(self.profile_tab, state="normal")
            self.notebook.tab(self.password_tab, state="normal")
            self.notebook.tab(self.admin_tab, state="normal" if role == "QuanTriVien" else "hidden")
            self._populate_profile(u)
            if role == "QuanTriVien" and self._admin_view is not None:
                self._admin_view.refresh_all()
        else:
            self.session_lbl.config(text="Trạng thái: Chưa đăng nhập", foreground="#475569")
            self.logout_btn.config(state="disabled")
            self.notebook.tab(self.profile_tab, state="disabled")
            self.notebook.tab(self.password_tab, state="disabled")
            self.notebook.tab(self.admin_tab, state="hidden")

    def _populate_profile(self, user: dict) -> None:
        self.prof_name.set(user.get("HoTen") or "")
        self.prof_mssv.set(user.get("MaSinhVien") or "")
        self.prof_phone.set(user.get("SoDienThoai") or "")
        self.prof_avatar.set(user.get("AnhDaiDien") or "")
        self.prof_bio.set(user.get("GioiThieu") or "")

        priv = user.get("CaiDatRiengTu") or {}
        self.priv_sdt.set(priv.get("hienSdt", "BanBe"))
        self.priv_email.set(priv.get("hienEmail", "CongDong"))
        self.priv_post.set(priv.get("hienBaiViet", "CongDong"))

        chain = user.get("community_chain") or []
        if chain:
            chain_text = " › ".join(item.get("TenCongDong", "") for item in chain)
            self.prof_chain_lbl.config(text=f"Chuỗi cộng đồng: {chain_text}")
            self.prof_cascade.load_roots([int(item["MaCongDong"]) for item in chain])
        else:
            self.prof_chain_lbl.config(text="Chuỗi cộng đồng: (Chưa gắn lớp)")
            self.prof_cascade.load_roots()

    def _handle_login(self) -> None:
        email = self.login_email.get().strip()
        pw = self.login_pw.get()
        if not email or not pw:
            self._set_status("Vui lòng nhập đầy đủ Email và Mật khẩu.", True)
            return

        base = self.get_server_url()
        self._set_status("Đang đăng nhập...", False)

        def on_done(res):
            status, data = res
            if status == 200 and data.get("access_token"):
                self.access_token = data["access_token"]
                self.current_user = data.get("user")
                self._refresh_session_ui()
                self.notebook.select(
                    self.admin_tab if (self.current_user or {}).get("VaiTro") == "QuanTriVien" else self.profile_tab
                )
                self._set_status(data.get("message", "Đăng nhập thành công."), False)
                if self.on_auth_success:
                    self.on_auth_success(data)
            else:
                self._set_status(data.get("detail", f"Đăng nhập thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(f"{base}/api/m01/auth/login", "POST", {"email": email, "password": pw}), on_done)

    def _handle_register(self) -> None:
        pw = self.reg_pw.get()
        if pw != self.reg_pw2.get():
            self._set_status("Mật khẩu xác nhận không khớp.", True)
            return
        lop_id = self.reg_cascade.get_selected_lop_id()
        if lop_id is None:
            self._set_status("Vui lòng chọn đầy đủ đến cấp Lớp trước khi đăng ký.", True)
            return

        payload = {
            "ho_ten": self.reg_name.get().strip(),
            "email": self.reg_email.get().strip(),
            "password": pw,
            "ma_lop": lop_id,
            "ma_sinh_vien": self.reg_mssv.get().strip() or None,
            "so_dien_thoai": self.reg_phone.get().strip() or None,
        }
        base = self.get_server_url()
        self._set_status("Đang đăng ký tài khoản...", False)

        def on_done(res):
            status, data = res
            if status == 201 and data.get("access_token"):
                self.access_token = data["access_token"]
                self.current_user = data.get("user")
                self._refresh_session_ui()
                self.notebook.select(self.profile_tab)
                self._set_status(data.get("message", "Đăng ký thành công."), False)
                if self.on_auth_success:
                    self.on_auth_success(data)
            else:
                self._set_status(data.get("detail", f"Đăng ký thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(f"{base}/api/m01/auth/register", "POST", payload), on_done)

    def _handle_logout(self) -> None:
        if not self.access_token:
            return
        base = self.get_server_url()
        tok = self.access_token

        def on_done(_res):
            self.access_token = ""
            self.current_user = None
            self._refresh_session_ui()
            self.notebook.select(self.login_tab)
            self._set_status("Đã đăng xuất khỏi hệ thống.", False)

        self._run_async(lambda: http_json(f"{base}/api/m01/auth/logout", "POST", {}, token=tok), on_done)

    def _handle_request_otp(self) -> None:
        email = self.fp_email.get().strip()
        if not email:
            self._set_status("Vui lòng nhập email đã đăng ký.", True)
            return
        base = self.get_server_url()

        def on_done(res):
            status, data = res
            if status == 200:
                demo = data.get("demo_otp")
                hint = f"{data.get('message', '')}"
                if demo:
                    hint += f" | Mã OTP demo: {demo}"
                    self.fp_otp.set(demo)
                self.otp_hint_lbl.config(text=hint)
                self._set_status("Đã gửi yêu cầu OTP.", False)
            else:
                self._set_status(data.get("detail", f"Lỗi gửi OTP (HTTP {status})."), True)

        self._run_async(lambda: http_json(f"{base}/api/m01/auth/forgot-otp", "POST", {"email": email}), on_done)

    def _handle_reset_pw(self) -> None:
        email = self.fp_email.get().strip()
        otp = self.fp_otp.get().strip()
        new_pw = self.fp_new_pw.get()
        if not email or not otp or not new_pw:
            self._set_status("Vui lòng nhập đầy đủ Email, OTP và Mật khẩu mới.", True)
            return
        base = self.get_server_url()

        def on_done(res):
            status, data = res
            if status == 200:
                self.fp_otp.set("")
                self.fp_new_pw.set("")
                self.notebook.select(self.login_tab)
                self._set_status(data.get("message", "Đặt lại mật khẩu thành công."), False)
            else:
                self._set_status(data.get("detail", f"Đặt lại mật khẩu thất bại (HTTP {status})."), True)

        self._run_async(
            lambda: http_json(
                f"{base}/api/m01/auth/reset-pw",
                "POST",
                {"email": email, "otp": otp, "new_password": new_pw},
            ),
            on_done,
        )

    def _handle_refresh_profile(self) -> None:
        if not self.access_token:
            return
        base = self.get_server_url()
        tok = self.access_token

        def on_done(res):
            status, data = res
            if status == 200 and data.get("user"):
                self.current_user = data["user"]
                self._populate_profile(self.current_user)
                self._set_status("Đã tải lại thông tin hồ sơ.", False)
            else:
                self._set_status(data.get("detail", f"Không tải được hồ sơ (HTTP {status})."), True)

        self._run_async(lambda: http_json(f"{base}/api/m01/users/me", "GET", token=tok), on_done)

    def _handle_save_profile(self) -> None:
        if not self.access_token:
            return
        lop_id = self.prof_cascade.get_selected_lop_id()
        payload = {
            "ho_ten": self.prof_name.get().strip(),
            "ma_sinh_vien": self.prof_mssv.get().strip(),
            "so_dien_thoai": self.prof_phone.get().strip(),
            "anh_dai_dien": self.prof_avatar.get().strip(),
            "gioi_thieu": self.prof_bio.get().strip(),
            "cai_dat_rieng_tu": {
                "hienSdt": self.priv_sdt.get(),
                "hienEmail": self.priv_email.get(),
                "hienBaiViet": self.priv_post.get(),
            },
        }
        if lop_id is not None:
            payload["ma_lop"] = lop_id

        base = self.get_server_url()
        tok = self.access_token

        def on_done(res):
            status, data = res
            if status == 200 and data.get("user"):
                self.current_user = data["user"]
                self._refresh_session_ui()
                self._set_status(data.get("message", "Cập nhật hồ sơ thành công."), False)
            else:
                self._set_status(data.get("detail", f"Lưu hồ sơ thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(f"{base}/api/m01/users/profile", "PUT", payload, token=tok), on_done)

    def _handle_change_password(self) -> None:
        if not self.access_token:
            return
        new_pw = self.cp_new.get()
        if new_pw != self.cp_new2.get():
            self._set_status("Mật khẩu mới nhập lại không khớp.", True)
            return
        payload = {"old_password": self.cp_old.get(), "new_password": new_pw}
        base = self.get_server_url()
        tok = self.access_token

        def on_done(res):
            status, data = res
            if status == 200:
                self.cp_old.set("")
                self.cp_new.set("")
                self.cp_new2.set("")
                messagebox.showinfo("Thành công", data.get("message", "Đổi mật khẩu thành công."))
                self._set_status(data.get("message", "Đổi mật khẩu thành công."), False)
            else:
                self._set_status(data.get("detail", f"Đổi mật khẩu thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(f"{base}/api/m01/users/password", "PUT", payload, token=tok), on_done)
