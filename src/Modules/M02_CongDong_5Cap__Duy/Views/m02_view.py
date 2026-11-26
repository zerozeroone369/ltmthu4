"""Tkinter Desktop View cho M2: Cây Cộng đồng 5 Cấp (Trường → Lớp) (Duy)."""
from __future__ import annotations

import tkinter as tk
import urllib.parse
from tkinter import messagebox, ttk

from src.Modules.M01_Auth_TaiKhoan__TuAnh.Views.http_helper import http_json

from .view_helpers import SessionAwareViewMixin

_LEVELS = [
    ("Truong", "Trường"),
    ("Khoa", "Khoa"),
    ("Nganh", "Ngành"),
    ("KhoaHoc", "Khóa học"),
    ("Lop", "Lớp"),
]
_EXPECTED_PARENT = {
    "Truong": None,
    "Khoa": "Truong",
    "Nganh": "Khoa",
    "KhoaHoc": "Nganh",
    "Lop": "KhoaHoc",
}
_LEVEL_LABEL = dict(_LEVELS)


class Module02View(SessionAwareViewMixin, ttk.Frame):
    """Màn hình Desktop Tkinter cho M2 — duyệt cây 5 cấp & quản trị đơn vị."""

    def __init__(
        self,
        parent,
        server_url: str = "http://127.0.0.1:8000",
        auth_token: str = "",
        get_token=None,
        get_server_url=None,
    ):
        super().__init__(parent, padding=10)
        self._init_session_binding(
            server_url=server_url,
            auth_token=auth_token,
            get_token=get_token,
            get_server_url=get_server_url,
        )

        self._level_items: list[list[dict]] = [[] for _ in _LEVELS]
        self._all_items_by_id: dict[int, dict] = {}
        self._parent_choices: list[dict] = []

        self._build_header()
        self._build_notebook()
        self.after(200, self.refresh_browser)

    def _build_header(self) -> None:
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", pady=(0, 6))

        left = ttk.Frame(hdr)
        left.pack(side="left", fill="x", expand=True)
        ttk.Label(
            left,
            text="M2: Cây Cộng đồng 5 Cấp (Trường → Khoa → Ngành → Khóa → Lớp)",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            left,
            text="Phụ trách: Duy • Dữ liệu thống nhất 1 bảng CongDong tự tham chiếu MaCongDongCha",
            foreground="#2563eb",
        ).pack(anchor="w")

        right = ttk.Frame(hdr)
        right.pack(side="right")
        ttk.Button(right, text="Tải lại Cây 5 cấp", command=self.refresh_browser).pack(side="left")

        self.status_lbl = ttk.Label(self, text="Sẵn sàng kết nối API /api/m02.", foreground="#475569")
        self.status_lbl.pack(fill="x", pady=(0, 6))

    def _build_notebook(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.browse_tab = ttk.Frame(self.notebook, padding=10)
        self.admin_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.browse_tab, text="Chọn & Xem Cây 5 Cấp")
        self.notebook.add(self.admin_tab, text="Quản trị Đơn vị (Admin)")

        self._build_browse_tab()
        self._build_admin_tab()

    def _build_browse_tab(self) -> None:
        cascade_box = ttk.LabelFrame(
            self.browse_tab,
            text="Bộ lọc nối tiếp 5 cấp (Cascading Trường → Lớp)",
            padding=10,
        )
        cascade_box.pack(fill="x", pady=(0, 8))

        self._combo_vars: list[tk.StringVar] = []
        self._combos: list[ttk.Combobox] = []
        for idx, (_code, label) in enumerate(_LEVELS):
            r = idx // 2
            c = (idx % 2) * 2
            ttk.Label(cascade_box, text=f"{label}:").grid(row=r, column=c, sticky="w", padx=(0, 6), pady=3)
            var = tk.StringVar()
            combo = ttk.Combobox(cascade_box, textvariable=var, state="readonly", width=30)
            combo.grid(row=r, column=c + 1, sticky="ew", padx=(0, 14), pady=3)
            combo.bind("<<ComboboxSelected>>", lambda _e, level_idx=idx: self._on_cascade_select(level_idx))
            self._combo_vars.append(var)
            self._combos.append(combo)

        cascade_box.columnconfigure(1, weight=1)
        cascade_box.columnconfigure(3, weight=1)

        self.chain_lbl = ttk.Label(
            cascade_box,
            text="Chuỗi phân cấp: (Chọn một đơn vị bên trên hoặc trong cây)",
            foreground="#1d4ed8",
            wraplength=800,
        )
        self.chain_lbl.grid(row=3, column=0, columnspan=4, sticky="w", pady=(6, 0))

        tree_box = ttk.LabelFrame(self.browse_tab, text="Cây cấu trúc Cộng đồng", padding=8)
        tree_box.pack(fill="both", expand=True)

        cols = ("cap_do", "ky_hieu", "nam", "trang_thai")
        self.tree_view = ttk.Treeview(tree_box, columns=cols, show="tree headings", height=11)
        self.tree_view.heading("#0", text="Tên Cộng đồng")
        self.tree_view.heading("cap_do", text="Cấp độ")
        self.tree_view.heading("ky_hieu", text="Ký hiệu")
        self.tree_view.heading("nam", text="Khóa năm")
        self.tree_view.heading("trang_thai", text="Trạng thái")

        self.tree_view.column("#0", width=280)
        self.tree_view.column("cap_do", width=90)
        self.tree_view.column("ky_hieu", width=110)
        self.tree_view.column("nam", width=80)
        self.tree_view.column("trang_thai", width=110)
        self.tree_view.pack(side="left", fill="both", expand=True)
        self.tree_view.bind("<<TreeviewSelect>>", self._on_tree_select)

        sb = ttk.Scrollbar(tree_box, orient="vertical", command=self.tree_view.yview)
        sb.pack(side="right", fill="y")
        self.tree_view.configure(yscrollcommand=sb.set)

    def _build_admin_tab(self) -> None:
        top_bar = ttk.Frame(self.admin_tab)
        top_bar.pack(fill="x", pady=(0, 6))

        ttk.Label(top_bar, text="Lọc cấp:").pack(side="left")
        self.f_level = tk.StringVar(value="Tất cả")
        ttk.Combobox(
            top_bar,
            textvariable=self.f_level,
            values=["Tất cả", *[c for c, _ in _LEVELS]],
            state="readonly",
            width=12,
        ).pack(side="left", padx=(4, 10))

        ttk.Label(top_bar, text="Từ khóa:").pack(side="left")
        self.f_search = tk.StringVar()
        ttk.Entry(top_bar, textvariable=self.f_search, width=20).pack(side="left", padx=(4, 10))

        ttk.Label(top_bar, text="Token Admin (nếu chạy lẻ):").pack(side="left")
        self.manual_token_var = tk.StringVar()
        ttk.Entry(top_bar, textvariable=self.manual_token_var, width=18, show="*").pack(side="left", padx=(4, 8))
        ttk.Button(top_bar, text="Tải danh sách Admin", command=self.load_admin_list).pack(side="left")

        cols = ("id", "cap_do", "ky_hieu", "ten", "cha", "nam", "trang_thai")
        self.admin_tree = ttk.Treeview(self.admin_tab, columns=cols, show="headings", height=7)
        headings = [
            ("id", "Mã", 50),
            ("cap_do", "Cấp độ", 85),
            ("ky_hieu", "Ký hiệu", 95),
            ("ten", "Tên Cộng đồng", 230),
            ("cha", "Mã Cha", 65),
            ("nam", "Năm", 55),
            ("trang_thai", "Trạng thái", 110),
        ]
        for key, title, width in headings:
            self.admin_tree.heading(key, text=title)
            self.admin_tree.column(key, width=width)
        self.admin_tree.pack(fill="both", expand=True, pady=(0, 8))
        self.admin_tree.bind("<<TreeviewSelect>>", self._on_admin_row_select)

        form = ttk.LabelFrame(self.admin_tab, text="Thêm mới / Chỉnh sửa đơn vị Cộng đồng", padding=8)
        form.pack(fill="x")

        self.edit_id_var = tk.StringVar(value="")
        self.form_level = tk.StringVar(value="Lop")
        self.form_parent = tk.StringVar(value="")
        self.form_code = tk.StringVar()
        self.form_name = tk.StringVar()
        self.form_year = tk.StringVar()
        self.form_status = tk.StringVar(value="DangHoatDong")
        self.cascade_disable = tk.BooleanVar(value=True)

        ttk.Label(form, text="Đang chọn ID:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Label(form, textvariable=self.edit_id_var, foreground="#2563eb").grid(row=0, column=1, sticky="w", pady=3)

        ttk.Label(form, text="Cấp độ:").grid(row=0, column=2, sticky="w", padx=(12, 4), pady=3)
        level_cb = ttk.Combobox(
            form,
            textvariable=self.form_level,
            values=[c for c, _ in _LEVELS],
            state="readonly",
            width=14,
        )
        level_cb.grid(row=0, column=3, sticky="w", pady=3)
        level_cb.bind("<<ComboboxSelected>>", lambda _e: self._sync_parent_choices())

        ttk.Label(form, text="Đơn vị cha:").grid(row=1, column=0, sticky="w", pady=3)
        self.parent_cb = ttk.Combobox(form, textvariable=self.form_parent, state="readonly", width=36)
        self.parent_cb.grid(row=1, column=1, columnspan=3, sticky="ew", pady=3)

        ttk.Label(form, text="Ký hiệu:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.form_code, width=18).grid(row=2, column=1, sticky="w", pady=3)

        ttk.Label(form, text="Tên đơn vị (*):").grid(row=2, column=2, sticky="w", padx=(12, 4), pady=3)
        ttk.Entry(form, textvariable=self.form_name, width=30).grid(row=2, column=3, sticky="ew", pady=3)

        ttk.Label(form, text="Năm bắt đầu:").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.form_year, width=12).grid(row=3, column=1, sticky="w", pady=3)

        ttk.Label(form, text="Trạng thái:").grid(row=3, column=2, sticky="w", padx=(12, 4), pady=3)
        ttk.Combobox(
            form,
            textvariable=self.form_status,
            values=["DangHoatDong", "NgungHoatDong"],
            state="readonly",
            width=16,
        ).grid(row=3, column=3, sticky="w", pady=3)

        form.columnconfigure(3, weight=1)

        btns = ttk.Frame(form)
        btns.grid(row=4, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(btns, text="Tạo mới đơn vị", command=self._handle_create_unit).pack(side="left")
        ttk.Button(btns, text="Lưu cập nhật", command=self._handle_update_unit).pack(side="left", padx=6)
        ttk.Button(btns, text="Tạm ngưng đơn vị", command=self._handle_deactivate_unit).pack(side="left")
        ttk.Checkbutton(btns, text="Ngưng cả cấp con", variable=self.cascade_disable).pack(side="left", padx=6)
        ttk.Button(btns, text="Xóa trắng form", command=self._clear_form).pack(side="left", padx=6)

    def refresh_browser(self) -> None:
        self._load_cascade_level(0, None)
        self._load_full_tree()
        if self._token():
            self.load_admin_list()

    def _load_cascade_level(self, level_idx: int, parent_id: int | None) -> None:
        base = self._server_url()
        url = (
            f"{base}/api/m02/communities/roots"
            if parent_id is None
            else f"{base}/api/m02/communities/{parent_id}/children"
        )

        def on_done(res):
            status, data = res
            if status != 200:
                self._set_status(data.get("detail", f"Không tải được cấp {_LEVELS[level_idx][1]} (HTTP {status})."), True)
                return
            items = data.get("items", [])
            self._level_items[level_idx] = items
            self._combos[level_idx]["values"] = [
                f"{it.get('TenCongDong', '')} ({it.get('KyHieu') or it['MaCongDong']})" for it in items
            ]
            for j in range(level_idx + 1, len(_LEVELS)):
                self._level_items[j] = []
                self._combo_vars[j].set("")
                self._combos[j]["values"] = []

            if items:
                self._combos[level_idx].current(0)
                chosen = items[0]
                if level_idx + 1 < len(_LEVELS):
                    self._load_cascade_level(level_idx + 1, int(chosen["MaCongDong"]))
                else:
                    self._fetch_chain_label(int(chosen["MaCongDong"]))
            else:
                self._combo_vars[level_idx].set("")

        self._run_async(lambda: http_json(url, "GET"), on_done)

    def _on_cascade_select(self, level_idx: int) -> None:
        sel = self._combos[level_idx].current()
        items = self._level_items[level_idx]
        if sel < 0 or sel >= len(items):
            return
        selected = items[sel]
        cid = int(selected["MaCongDong"])
        self._fetch_chain_label(cid)
        if level_idx + 1 < len(_LEVELS):
            self._load_cascade_level(level_idx + 1, cid)

    def _fetch_chain_label(self, community_id: int) -> None:
        base = self._server_url()

        def on_done(res):
            status, data = res
            if status == 200 and data.get("chain"):
                text = " › ".join(
                    f"[{_LEVEL_LABEL.get(item['CapDo'], item['CapDo'])}] {item['TenCongDong']}"
                    for item in data["chain"]
                )
                self.chain_lbl.config(text=f"Chuỗi phân cấp: {text}")

        self._run_async(lambda: http_json(f"{base}/api/m02/communities/chain/{community_id}", "GET"), on_done)

    def _load_full_tree(self) -> None:
        base = self._server_url()

        def on_done(res):
            status, data = res
            if status != 200:
                return
            for root_iid in self.tree_view.get_children():
                self.tree_view.delete(root_iid)
            self._all_items_by_id.clear()
            for item in data.get("items", []):
                self._all_items_by_id[int(item["MaCongDong"])] = item
            self._insert_tree_nodes("", data.get("tree", []))
            self._sync_parent_choices()

        self._run_async(lambda: http_json(f"{base}/api/m02/communities/tree", "GET"), on_done)

    def _insert_tree_nodes(self, parent_iid: str, nodes: list[dict]) -> None:
        for node in nodes:
            iid = str(node["MaCongDong"])
            self.tree_view.insert(
                parent_iid,
                "end",
                iid=iid,
                text=node.get("TenCongDong") or "",
                open=True,
                values=(
                    _LEVEL_LABEL.get(node.get("CapDo", ""), node.get("CapDo", "")),
                    node.get("KyHieu") or "-",
                    node.get("NamBatDau") or "-",
                    node.get("TrangThai") or "",
                ),
            )
            self._insert_tree_nodes(iid, node.get("children", []))

    def _on_tree_select(self, _event=None) -> None:
        sel = self.tree_view.selection()
        if sel:
            self._fetch_chain_label(int(sel[0]))

    def load_admin_list(self) -> None:
        tok = self._token()
        if not tok:
            self._set_status("Cần token QuanTriVien (hoặc đăng nhập ở M1 trước) để tải danh sách Admin.", True)
            return

        params: dict[str, str] = {}
        if self.f_level.get() != "Tất cả":
            params["cap_do"] = self.f_level.get()
        if self.f_search.get().strip():
            params["search"] = self.f_search.get().strip()
        qs = f"?{urllib.parse.urlencode(params)}" if params else ""
        url = f"{self._server_url()}/api/m02/admin/communities{qs}"

        def on_done(res):
            status, data = res
            if status != 200:
                self._set_status(data.get("detail", f"Không tải được danh sách Admin (HTTP {status})."), True)
                return
            for iid in self.admin_tree.get_children():
                self.admin_tree.delete(iid)
            for item in data.get("items", []):
                cid = int(item["MaCongDong"])
                self._all_items_by_id[cid] = item
                self.admin_tree.insert(
                    "",
                    "end",
                    iid=str(cid),
                    values=(
                        cid,
                        item.get("CapDo") or "",
                        item.get("KyHieu") or "-",
                        item.get("TenCongDong") or "",
                        item.get("MaCongDongCha") or "-",
                        item.get("NamBatDau") or "-",
                        item.get("TrangThai") or "",
                    ),
                )
            self._sync_parent_choices()
            self._set_status(f"Đã tải {len(data.get('items', []))} đơn vị cộng đồng.", False)

        self._run_async(lambda: http_json(url, "GET", token=tok), on_done)

    def _sync_parent_choices(self) -> None:
        cap = self.form_level.get()
        expected = _EXPECTED_PARENT.get(cap)
        if expected is None:
            self._parent_choices = []
            self.parent_cb["values"] = ["(Không có - cấp Trường)"]
            self.form_parent.set("(Không có - cấp Trường)")
            return
        candidates = [it for it in self._all_items_by_id.values() if it.get("CapDo") == expected]
        self._parent_choices = candidates
        labels = [f"#{it['MaCongDong']} - {it['TenCongDong']} ({it.get('KyHieu') or '-'})" for it in candidates]
        self.parent_cb["values"] = labels
        if labels and self.form_parent.get() not in labels:
            self.parent_cb.current(0)

    def _selected_parent_id(self) -> int | None:
        if _EXPECTED_PARENT.get(self.form_level.get()) is None:
            return None
        idx = self.parent_cb.current()
        if 0 <= idx < len(self._parent_choices):
            return int(self._parent_choices[idx]["MaCongDong"])
        return None

    def _on_admin_row_select(self, _event=None) -> None:
        sel = self.admin_tree.selection()
        if not sel:
            return
        item = self._all_items_by_id.get(int(sel[0]))
        if not item:
            return
        self.edit_id_var.set(str(item["MaCongDong"]))
        self.form_level.set(item.get("CapDo", "Lop"))
        self._sync_parent_choices()
        parent_id = item.get("MaCongDongCha")
        if parent_id is not None:
            for idx, cand in enumerate(self._parent_choices):
                if int(cand["MaCongDong"]) == int(parent_id):
                    self.parent_cb.current(idx)
                    break
        self.form_code.set(item.get("KyHieu") or "")
        self.form_name.set(item.get("TenCongDong") or "")
        self.form_year.set("" if item.get("NamBatDau") is None else str(item["NamBatDau"]))
        self.form_status.set(item.get("TrangThai") or "DangHoatDong")

    def _clear_form(self) -> None:
        self.edit_id_var.set("")
        self.form_code.set("")
        self.form_name.set("")
        self.form_year.set("")
        self.form_status.set("DangHoatDong")

    def _parse_year(self) -> int | None:
        raw = self.form_year.get().strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            self._set_status("Năm bắt đầu phải là số nguyên.", True)
            return -1

    def _handle_create_unit(self) -> None:
        tok = self._token()
        if not tok:
            self._set_status("Cần token QuanTriVien để tạo đơn vị mới.", True)
            return
        year_val = self._parse_year()
        if year_val == -1:
            return
        payload = {
            "cap_do": self.form_level.get(),
            "ma_cong_dong_cha": self._selected_parent_id(),
            "ky_hieu": self.form_code.get().strip() or None,
            "ten_cong_dong": self.form_name.get().strip(),
            "nam_bat_dau": year_val,
        }
        url = f"{self._server_url()}/api/m02/admin/communities"

        def on_done(res):
            status, data = res
            if status == 201:
                self._set_status(data.get("message", "Tạo đơn vị thành công."), False)
                self._clear_form()
                self.refresh_browser()
            else:
                self._set_status(data.get("detail", f"Tạo đơn vị thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "POST", payload, token=tok), on_done)

    def _handle_update_unit(self) -> None:
        tok = self._token()
        cid = self.edit_id_var.get().strip()
        if not tok or not cid:
            self._set_status("Chọn một đơn vị trong bảng Admin và đảm bảo đã đăng nhập Admin.", True)
            return
        year_val = self._parse_year()
        if year_val == -1:
            return
        payload = {
            "ten_cong_dong": self.form_name.get().strip(),
            "ky_hieu": self.form_code.get().strip(),
            "ma_cong_dong_cha": self._selected_parent_id(),
            "nam_bat_dau": year_val,
            "trang_thai": self.form_status.get(),
        }
        url = f"{self._server_url()}/api/m02/admin/communities/{cid}"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Cập nhật thành công."), False)
                self.refresh_browser()
            else:
                self._set_status(data.get("detail", f"Cập nhật thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "PUT", payload, token=tok), on_done)

    def _handle_deactivate_unit(self) -> None:
        tok = self._token()
        cid = self.edit_id_var.get().strip()
        if not tok or not cid:
            self._set_status("Chọn một đơn vị trong bảng Admin để tạm ngưng.", True)
            return
        if not messagebox.askyesno("Xác nhận", f"Tạm ngưng đơn vị #{cid}?"):
            return
        cascade_q = "true" if self.cascade_disable.get() else "false"
        url = f"{self._server_url()}/api/m02/admin/communities/{cid}?cascade={cascade_q}"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Đã tạm ngưng đơn vị."), False)
                self.refresh_browser()
            else:
                self._set_status(data.get("detail", f"Tạm ngưng thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "DELETE", token=tok), on_done)
