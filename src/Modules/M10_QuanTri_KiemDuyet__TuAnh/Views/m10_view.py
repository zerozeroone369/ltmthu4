"""Tkinter Desktop View cho M10: Quản trị Hệ thống & Kiểm duyệt (Admin) (Nguyễn Ngô Tú Anh)."""
from __future__ import annotations

import tkinter as tk
import urllib.parse
from tkinter import messagebox, ttk

from src.Modules.M01_Auth_TaiKhoan__TuAnh.Views.http_helper import (
    http_json,
    run_async_tk,
)
from src.Modules.M02_CongDong_5Cap__Duy.Views.m02_view import Module02View
from src.Modules.M07_Campus__Bao.Views.m07_view import Module07View


class Module10View(ttk.Frame):
    """Màn hình Desktop Tkinter (KHÔNG phải Web) cho M10: Admin Dashboard & Kiểm duyệt."""

    def __init__(
        self,
        parent,
        server_url: str = "http://127.0.0.1:8000",
        auth_token: str = "",
        get_token=None,
        get_server_url=None,
    ):
        super().__init__(parent, padding=10)
        self.server_url = server_url or "http://127.0.0.1:8000"
        self.auth_token = auth_token
        self._get_token_cb = get_token
        self._get_server_url_cb = get_server_url
        self._users_by_id: dict[int, dict] = {}
        self._reports_by_id: dict[int, dict] = {}

        self._build_header()
        self._build_notebook()

    def _server_url(self) -> str:
        if self._get_server_url_cb:
            return self._get_server_url_cb().rstrip("/")
        return self.server_url.strip().rstrip("/")

    def _token(self) -> str:
        if self._get_token_cb:
            return self._get_token_cb()
        return self.auth_token

    def _set_status(self, message: str, is_error: bool = False) -> None:
        self.status_lbl.config(text=message, foreground="#dc2626" if is_error else "#15803d")

    def _run_async(self, fn, on_done) -> None:
        run_async_tk(self, fn, on_done)

    def refresh_all(self) -> None:
        if self._token():
            self.load_users()
            self.load_reports()

    def _build_header(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 6))
        ttk.Label(
            top,
            text="M10: Quản trị Hệ thống & Kiểm duyệt Vi phạm (Admin Dashboard)",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        ttk.Button(top, text="Làm mới dữ liệu", command=self.refresh_all).pack(side="right")

        self.status_lbl = ttk.Label(self, text="Sẵn sàng quản trị khi đăng nhập bằng tài khoản QuanTriVien.", foreground="#475569")
        self.status_lbl.pack(fill="x", pady=(0, 6))

    def _build_notebook(self) -> None:
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        self.users_tab = ttk.Frame(self.nb, padding=8)
        self.reports_tab = ttk.Frame(self.nb, padding=8)
        self.m02_tab = ttk.Frame(self.nb, padding=8)
        self.m07_tab = ttk.Frame(self.nb, padding=8)

        self.nb.add(self.users_tab, text="Quản lý Tài khoản (NguoiDung)")
        self.nb.add(self.reports_tab, text="Kiểm duyệt Vi phạm (BaoCaoViPham)")
        self.nb.add(self.m02_tab, text="Cây Cộng đồng 5 Cấp (M02)")
        self.nb.add(self.m07_tab, text="Quản trị Campus (M07)")

        self._build_users_tab()
        self._build_reports_tab()
        self._embed_m02_m07()

    def _build_users_tab(self) -> None:
        flt = ttk.Frame(self.users_tab)
        flt.pack(fill="x", pady=(0, 6))

        self.u_search = tk.StringVar()
        self.u_role = tk.StringVar(value="Tất cả")
        self.u_status = tk.StringVar(value="Tất cả")

        ttk.Label(flt, text="Tìm kiếm:").pack(side="left")
        ttk.Entry(flt, textvariable=self.u_search, width=24).pack(side="left", padx=(4, 10))
        ttk.Label(flt, text="Vai trò:").pack(side="left")
        ttk.Combobox(
            flt,
            textvariable=self.u_role,
            values=["Tất cả", "SinhVien", "QuanTriVien"],
            state="readonly",
            width=12,
        ).pack(side="left", padx=(4, 10))
        ttk.Label(flt, text="Trạng thái:").pack(side="left")
        ttk.Combobox(
            flt,
            textvariable=self.u_status,
            values=["Tất cả", "HoatDong", "BiKhoa"],
            state="readonly",
            width=11,
        ).pack(side="left", padx=(4, 10))
        ttk.Button(flt, text="Lọc / Tải lại", command=self.load_users).pack(side="left")

        self.user_stats_lbl = ttk.Label(self.users_tab, text="Thống kê: --", foreground="#2563eb")
        self.user_stats_lbl.pack(anchor="w", pady=(0, 4))

        tree_wrap = ttk.Frame(self.users_tab)
        tree_wrap.pack(fill="both", expand=True)

        cols = ("MaNguoiDung", "HoTen", "Email", "MaSinhVien", "TenLop", "VaiTro", "TrangThai")
        self.users_tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", height=10)
        headers = {
            "MaNguoiDung": ("ID", 50),
            "HoTen": ("Họ tên", 160),
            "Email": ("Email", 190),
            "MaSinhVien": ("MSSV", 95),
            "TenLop": ("Lớp", 120),
            "VaiTro": ("Vai trò", 100),
            "TrangThai": ("Trạng thái", 95),
        }
        for col, (text, width) in headers.items():
            self.users_tree.heading(col, text=text)
            self.users_tree.column(col, width=width, anchor="w")

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=vsb.set)
        self.users_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        actions = ttk.Frame(self.users_tab)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Khóa tài khoản", command=lambda: self._update_selected_user_lock("BiKhoa")).pack(side="left")
        ttk.Button(actions, text="Mở khóa tài khoản", command=lambda: self._update_selected_user_lock("HoatDong")).pack(side="left", padx=6)
        ttk.Button(actions, text="Cấp quyền Admin", command=lambda: self._update_selected_user_role("QuanTriVien")).pack(side="left", padx=(16, 6))
        ttk.Button(actions, text="Chuyển về SinhVien", command=lambda: self._update_selected_user_role("SinhVien")).pack(side="left")

    def _build_reports_tab(self) -> None:
        flt = ttk.Frame(self.reports_tab)
        flt.pack(fill="x", pady=(0, 6))

        self.r_status = tk.StringVar(value="Tất cả")
        self.r_type = tk.StringVar(value="Tất cả")

        ttk.Label(flt, text="Trạng thái:").pack(side="left")
        ttk.Combobox(
            flt,
            textvariable=self.r_status,
            values=["Tất cả", "ChoDuyet", "DaXuLy", "TuChoi"],
            state="readonly",
            width=12,
        ).pack(side="left", padx=(4, 10))
        ttk.Label(flt, text="Loại nội dung:").pack(side="left")
        ttk.Combobox(
            flt,
            textvariable=self.r_type,
            values=["Tất cả", "BaiViet", "BinhLuan", "TaiLieu", "CauHoi", "CauTraLoi", "TinTruong", "NhomHoc", "NguoiDung"],
            state="readonly",
            width=13,
        ).pack(side="left", padx=(4, 10))
        ttk.Button(flt, text="Tải danh sách báo cáo", command=self.load_reports).pack(side="left")

        self.report_stats_lbl = ttk.Label(self.reports_tab, text="Thống kê đơn báo cáo: --", foreground="#2563eb")
        self.report_stats_lbl.pack(anchor="w", pady=(0, 4))

        tree_wrap = ttk.Frame(self.reports_tab)
        tree_wrap.pack(fill="both", expand=True)

        cols = ("MaBaoCao", "LoaiNoiDung", "IdNoiDung", "TenNguoiBaoCao", "LyDo", "TrangThai", "QuyetDinh")
        self.reports_tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", height=8)
        headers = {
            "MaBaoCao": ("ID", 50),
            "LoaiNoiDung": ("Loại", 95),
            "IdNoiDung": ("ID Nội dung", 85),
            "TenNguoiBaoCao": ("Người báo cáo", 145),
            "LyDo": ("Lý do", 200),
            "TrangThai": ("Trạng thái", 95),
            "QuyetDinh": ("Quyết định", 110),
        }
        for col, (text, width) in headers.items():
            self.reports_tree.heading(col, text=text)
            self.reports_tree.column(col, width=width, anchor="w")

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=vsb.set)
        self.reports_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.reports_tree.bind("<<TreeviewSelect>>", self._on_select_report)

        detail_box = ttk.LabelFrame(self.reports_tab, text="Chi tiết & Quyết định kiểm duyệt", padding=8)
        detail_box.pack(fill="x", pady=(8, 0))

        self.report_detail_lbl = ttk.Label(detail_box, text="Chọn một đơn báo cáo phía trên để xem chi tiết.", wraplength=800)
        self.report_detail_lbl.pack(anchor="w", pady=(0, 6))

        note_row = ttk.Frame(detail_box)
        note_row.pack(fill="x", pady=(0, 6))
        ttk.Label(note_row, text="Ghi chú xử lý:").pack(side="left")
        self.r_note = tk.StringVar()
        ttk.Entry(note_row, textvariable=self.r_note, width=60).pack(side="left", fill="x", expand=True, padx=8)

        btn_row = ttk.Frame(detail_box)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Bác bỏ", command=lambda: self._moderate_selected_report("BacBo")).pack(side="left")
        ttk.Button(btn_row, text="Ẩn nội dung", command=lambda: self._moderate_selected_report("AnNoiDung")).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Xóa mềm", command=lambda: self._moderate_selected_report("XoaMem")).pack(side="left")
        ttk.Button(btn_row, text="Khóa tài khoản vi phạm", command=lambda: self._moderate_selected_report("KhoaTaiKhoan")).pack(side="left", padx=6)

    def _embed_m02_m07(self) -> None:
        try:
            m02 = Module02View(self.m02_tab, server_url=self._server_url())
            m02.pack(fill="both", expand=True)
        except (tk.TclError, RuntimeError) as exc:
            ttk.Label(self.m02_tab, text=f"Không thể nhúng Module02View: {exc}", foreground="#dc2626").pack(anchor="w")

        try:
            m07 = Module07View(self.m07_tab, server_url=self._server_url())
            m07.pack(fill="both", expand=True)
        except (tk.TclError, RuntimeError) as exc:
            ttk.Label(self.m07_tab, text=f"Không thể nhúng Module07View: {exc}", foreground="#dc2626").pack(anchor="w")

    def load_users(self) -> None:
        tok = self._token()
        if not tok:
            self._set_status("Cần đăng nhập tài khoản QuanTriVien để tải danh sách tài khoản.", True)
            return

        params: dict[str, str] = {}
        if self.u_search.get().strip():
            params["search"] = self.u_search.get().strip()
        if self.u_role.get() != "Tất cả":
            params["vai_tro"] = self.u_role.get()
        if self.u_status.get() != "Tất cả":
            params["trang_thai"] = self.u_status.get()
        qs = f"?{urllib.parse.urlencode(params)}" if params else ""
        url = f"{self._server_url()}/api/m10/admin/users{qs}"

        def on_done(res):
            status, data = res
            if status != 200:
                self._set_status(data.get("detail", f"Không tải được tài khoản (HTTP {status})."), True)
                return
            for iid in self.users_tree.get_children():
                self.users_tree.delete(iid)
            self._users_by_id.clear()
            for row in data.get("items", []):
                uid = int(row["MaNguoiDung"])
                self._users_by_id[uid] = row
                self.users_tree.insert(
                    "",
                    "end",
                    iid=str(uid),
                    values=(
                        uid,
                        row.get("HoTen") or "",
                        row.get("Email") or "",
                        row.get("MaSinhVien") or "",
                        row.get("TenLop") or "-",
                        row.get("VaiTro") or "",
                        row.get("TrangThai") or "",
                    ),
                )
            st = data.get("stats") or {}
            self.user_stats_lbl.config(
                text=f"Tổng: {st.get('total_users', 0)} • Admin hoạt động: {st.get('active_admins', 0)} • Bị khóa: {st.get('locked_users', 0)}"
            )
            self._set_status(f"Đã tải {len(data.get('items', []))} tài khoản.", False)

        self._run_async(lambda: http_json(url, "GET", token=tok), on_done)

    def _update_selected_user_lock(self, trang_thai: str) -> None:
        sel = self.users_tree.selection()
        if not sel:
            self._set_status("Vui lòng chọn một tài khoản trong bảng.", True)
            return
        uid = int(sel[0])
        user = self._users_by_id.get(uid, {})
        action_txt = "khóa" if trang_thai == "BiKhoa" else "mở khóa"
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn {action_txt} tài khoản '{user.get('HoTen', uid)}'?"):
            return

        tok = self._token()
        url = f"{self._server_url()}/api/m10/admin/users/{uid}/lock"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Cập nhật trạng thái thành công."), False)
                self.load_users()
            else:
                msg = data.get("detail", f"Thao tác thất bại (HTTP {status}).")
                messagebox.showerror("Không thể thực hiện", msg)
                self._set_status(msg, True)

        self._run_async(lambda: http_json(url, "PUT", {"trang_thai": trang_thai}, token=tok), on_done)

    def _update_selected_user_role(self, vai_tro: str) -> None:
        sel = self.users_tree.selection()
        if not sel:
            self._set_status("Vui lòng chọn một tài khoản trong bảng.", True)
            return
        uid = int(sel[0])
        user = self._users_by_id.get(uid, {})
        if not messagebox.askyesno("Xác nhận đổi vai trò", f"Đổi vai trò của '{user.get('HoTen', uid)}' thành '{vai_tro}'?"):
            return

        tok = self._token()
        url = f"{self._server_url()}/api/m10/admin/users/{uid}/role"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Đổi vai trò thành công."), False)
                self.load_users()
            else:
                msg = data.get("detail", f"Đổi vai trò thất bại (HTTP {status}).")
                messagebox.showerror("Không thể thực hiện", msg)
                self._set_status(msg, True)

        self._run_async(lambda: http_json(url, "PUT", {"vai_tro": vai_tro}, token=tok), on_done)

    def load_reports(self) -> None:
        tok = self._token()
        if not tok:
            self._set_status("Cần đăng nhập tài khoản QuanTriVien để xem đơn báo cáo.", True)
            return

        params: dict[str, str] = {}
        if self.r_status.get() != "Tất cả":
            params["trang_thai"] = self.r_status.get()
        if self.r_type.get() != "Tất cả":
            params["loai_noi_dung"] = self.r_type.get()
        qs = f"?{urllib.parse.urlencode(params)}" if params else ""
        url = f"{self._server_url()}/api/m10/admin/reports{qs}"

        def on_done(res):
            status, data = res
            if status != 200:
                self._set_status(data.get("detail", f"Không tải được báo cáo (HTTP {status})."), True)
                return
            for iid in self.reports_tree.get_children():
                self.reports_tree.delete(iid)
            self._reports_by_id.clear()
            for row in data.get("items", []):
                rid = int(row["MaBaoCao"])
                self._reports_by_id[rid] = row
                self.reports_tree.insert(
                    "",
                    "end",
                    iid=str(rid),
                    values=(
                        rid,
                        row.get("LoaiNoiDung") or "",
                        row.get("IdNoiDung") or "",
                        row.get("TenNguoiBaoCao") or "",
                        row.get("LyDo") or "",
                        row.get("TrangThai") or "",
                        row.get("QuyetDinh") or "-",
                    ),
                )
            st = data.get("stats") or {}
            self.report_stats_lbl.config(
                text=f"Chờ duyệt: {st.get('cho_duyet', 0)} • Đã xử lý: {st.get('da_xu_ly', 0)} • Từ chối: {st.get('tu_choi', 0)}"
            )
            self._set_status(f"Đã tải {len(data.get('items', []))} báo cáo vi phạm.", False)

        self._run_async(lambda: http_json(url, "GET", token=tok), on_done)

    def _on_select_report(self, _event=None) -> None:
        sel = self.reports_tree.selection()
        if not sel:
            return
        rep = self._reports_by_id.get(int(sel[0]))
        if not rep:
            return
        detail = (
            f"Báo cáo #{rep['MaBaoCao']} • {rep['LoaiNoiDung']} #{rep['IdNoiDung']} | "
            f"Người gửi: {rep.get('TenNguoiBaoCao')} | Trạng thái: {rep.get('TrangThai')}\n"
            f"Chi tiết: {rep.get('ChiTiet') or '(Không có)'} | "
            f"Admin xử lý: {rep.get('TenAdminXuLy') or '(Chưa xử lý)'}"
        )
        self.report_detail_lbl.config(text=detail)
        if rep.get("GhiChuXuLy"):
            self.r_note.set(rep["GhiChuXuLy"])

    def _moderate_selected_report(self, quyet_dinh: str) -> None:
        sel = self.reports_tree.selection()
        if not sel:
            self._set_status("Vui lòng chọn một đơn báo cáo để xử lý.", True)
            return
        rid = int(sel[0])
        if not messagebox.askyesno("Xác nhận kiểm duyệt", f"Áp dụng quyết định '{quyet_dinh}' cho báo cáo #{rid}?"):
            return

        tok = self._token()
        url = f"{self._server_url()}/api/m10/admin/reports/{rid}"
        payload = {"quyet_dinh": quyet_dinh, "ghi_chu_xu_ly": self.r_note.get().strip() or None}

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Xử lý báo cáo thành công."), False)
                self.r_note.set("")
                self.load_reports()
                self.load_users()
            else:
                msg = data.get("detail", f"Xử lý báo cáo thất bại (HTTP {status}).")
                messagebox.showerror("Không thể xử lý", msg)
                self._set_status(msg, True)

        self._run_async(lambda: http_json(url, "PUT", payload, token=tok), on_done)
