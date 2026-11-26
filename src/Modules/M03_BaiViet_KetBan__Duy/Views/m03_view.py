"""Tkinter Desktop View cho M3: Bài viết, Tương tác & Kết bạn (Duy)."""
from __future__ import annotations

import tkinter as tk
import urllib.parse
from tkinter import filedialog, messagebox, ttk

from src.Modules.M01_Auth_TaiKhoan__TuAnh.Views.http_helper import http_json
from src.Modules.M02_CongDong_5Cap__Duy.Views.view_helpers import SessionAwareViewMixin

_CATEGORIES = ["HocTap", "ChiaSe", "ThaoLuan", "HoiDap", "Khac"]


class Module03View(SessionAwareViewMixin, ttk.Frame):
    """Màn hình Desktop Tkinter cho M3 — Đăng/Sửa/Xóa bài, Bình luận/Thích & Kết bạn."""

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

        self._communities: list[dict] = []
        self._posts_by_id: dict[int, dict] = {}
        self._selected_post_id: int | None = None
        self._search_users_by_id: dict[int, dict] = {}

        self._build_header()
        self._build_notebook()
        self.after(250, self.refresh_all)

    def _build_header(self) -> None:
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", pady=(0, 6))

        left = ttk.Frame(hdr)
        left.pack(side="left", fill="x", expand=True)
        ttk.Label(
            left,
            text="M3: Bài viết Cộng đồng, Bình luận/Thích & Kết bạn 2 chiều",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            left,
            text="Phụ trách: Duy • Bảng PostgreSQL: BaiViet, BinhLuan, TuongTac, KetBan",
            foreground="#2563eb",
        ).pack(anchor="w")

        right = ttk.Frame(hdr)
        right.pack(side="right")
        ttk.Label(right, text="Token (nếu chạy lẻ):").pack(side="left")
        self.manual_token_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.manual_token_var, width=20, show="*").pack(side="left", padx=(4, 8))
        ttk.Button(right, text="Làm mới", command=self.refresh_all).pack(side="left")

        self.status_lbl = ttk.Label(self, text="Sẵn sàng khi đã đăng nhập tài khoản Sinh viên/Admin.", foreground="#475569")
        self.status_lbl.pack(fill="x", pady=(0, 6))

    def _build_notebook(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.posts_tab = ttk.Frame(self.notebook, padding=10)
        self.friends_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.posts_tab, text="Bài viết & Tương tác")
        self.notebook.add(self.friends_tab, text="Tìm bạn & Kết bạn")

        self._build_posts_tab()
        self._build_friends_tab()

    def _build_posts_tab(self) -> None:
        composer = ttk.LabelFrame(self.posts_tab, text="Soạn / Chỉnh sửa Bài viết", padding=8)
        composer.pack(fill="x", pady=(0, 8))

        self.post_edit_id = tk.StringVar(value="")
        self.post_comm_var = tk.StringVar()
        self.post_cat_var = tk.StringVar(value="HocTap")
        self.post_attach_var = tk.StringVar()

        row0 = ttk.Frame(composer)
        row0.pack(fill="x", pady=(0, 4))
        ttk.Label(row0, text="Cộng đồng:").pack(side="left")
        self.post_comm_cb = ttk.Combobox(row0, textvariable=self.post_comm_var, state="readonly", width=34)
        self.post_comm_cb.pack(side="left", padx=(4, 12))

        ttk.Label(row0, text="Danh mục:").pack(side="left")
        ttk.Combobox(row0, textvariable=self.post_cat_var, values=_CATEGORIES, state="readonly", width=12).pack(
            side="left", padx=(4, 12)
        )
        ttk.Label(row0, text="Đính kèm:").pack(side="left")
        ttk.Entry(row0, textvariable=self.post_attach_var, width=24).pack(side="left", padx=4)
        ttk.Button(row0, text="Chọn tệp", command=self._choose_attachment).pack(side="left")

        self.post_text = tk.Text(composer, height=3, width=80, wrap="word")
        self.post_text.pack(fill="x", pady=4)

        btn_row = ttk.Frame(composer)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Đăng bài mới", command=self._handle_create_post).pack(side="left")
        ttk.Button(btn_row, text="Lưu chỉnh sửa", command=self._handle_update_post).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Xóa bài đang chọn", command=self._handle_delete_post).pack(side="left")
        ttk.Button(btn_row, text="Xóa trắng", command=self._clear_post_form).pack(side="left", padx=6)

        flt = ttk.Frame(self.posts_tab)
        flt.pack(fill="x", pady=(0, 4))
        ttk.Label(flt, text="Lọc bài viết:").pack(side="left")
        self.p_search = tk.StringVar()
        ttk.Entry(flt, textvariable=self.p_search, width=28).pack(side="left", padx=(6, 8))
        ttk.Button(flt, text="Tải danh sách bài viết", command=self.load_posts).pack(side="left")

        cols = ("id", "tac_gia", "cong_dong", "danh_muc", "thich", "binh_luan", "noi_dung")
        self.posts_tree = ttk.Treeview(self.posts_tab, columns=cols, show="headings", height=6)
        for key, label, width in [
            ("id", "Mã", 45),
            ("tac_gia", "Tác giả", 140),
            ("cong_dong", "Cộng đồng", 150),
            ("danh_muc", "Danh mục", 80),
            ("thich", "Thích", 55),
            ("binh_luan", "B.luận", 55),
            ("noi_dung", "Nội dung", 310),
        ]:
            self.posts_tree.heading(key, text=label)
            self.posts_tree.column(key, width=width)
        self.posts_tree.pack(fill="both", expand=True, pady=(0, 6))
        self.posts_tree.bind("<<TreeviewSelect>>", self._on_select_post)

        interact = ttk.LabelFrame(self.posts_tab, text="Chi tiết & Tương tác (Thích / Bình luận)", padding=8)
        interact.pack(fill="x")

        bar = ttk.Frame(interact)
        bar.pack(fill="x", pady=(0, 4))
        self.like_btn = ttk.Button(bar, text="Thích bài viết", command=self._handle_toggle_like)
        self.like_btn.pack(side="left")
        self.post_meta_lbl = ttk.Label(bar, text="Chọn một bài viết bên trên để xem bình luận.", foreground="#475569")
        self.post_meta_lbl.pack(side="left", padx=10)

        self.comments_list = tk.Listbox(interact, height=4)
        self.comments_list.pack(fill="x", pady=(0, 4))

        c_row = ttk.Frame(interact)
        c_row.pack(fill="x")
        self.comment_var = tk.StringVar()
        ttk.Entry(c_row, textvariable=self.comment_var, width=64).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(c_row, text="Gửi bình luận", command=self._handle_add_comment).pack(side="left")

    def _build_friends_tab(self) -> None:
        search_box = ttk.LabelFrame(self.friends_tab, text="Tìm bạn học & Gửi lời mời kết bạn", padding=8)
        search_box.pack(fill="x", pady=(0, 8))

        flt = ttk.Frame(search_box)
        flt.pack(fill="x", pady=(0, 6))
        ttk.Label(flt, text="Tên / MSSV / Email:").pack(side="left")
        self.f_query = tk.StringVar()
        ttk.Entry(flt, textvariable=self.f_query, width=32).pack(side="left", padx=(6, 8))
        ttk.Button(flt, text="Tìm kiếm", command=self.search_students).pack(side="left")
        ttk.Button(flt, text="Gửi lời mời kết bạn", command=self._handle_send_friend_request).pack(side="left", padx=8)

        cols = ("id", "ho_ten", "mssv", "lop", "quan_he")
        self.search_tree = ttk.Treeview(search_box, columns=cols, show="headings", height=5)
        for key, label, width in [
            ("id", "Mã SV", 60),
            ("ho_ten", "Họ và tên", 200),
            ("mssv", "MSSV", 110),
            ("lop", "Lớp", 190),
            ("quan_he", "Trạng thái quan hệ", 150),
        ]:
            self.search_tree.heading(key, text=label)
            self.search_tree.column(key, width=width)
        self.search_tree.pack(fill="x")

        rel_box = ttk.LabelFrame(self.friends_tab, text="Lời mời Kết bạn & Danh sách Bạn bè", padding=8)
        rel_box.pack(fill="both", expand=True)

        rel_cols = ("kb_id", "loai", "ho_ten", "mssv", "lop", "trang_thai")
        self.rel_tree = ttk.Treeview(rel_box, columns=rel_cols, show="headings", height=7)
        for key, label, width in [
            ("kb_id", "Mã KB", 60),
            ("loai", "Phân loại", 120),
            ("ho_ten", "Bạn học", 190),
            ("mssv", "MSSV", 110),
            ("lop", "Lớp", 160),
            ("trang_thai", "Trạng thái", 100),
        ]:
            self.rel_tree.heading(key, text=label)
            self.rel_tree.column(key, width=width)
        self.rel_tree.pack(fill="both", expand=True, pady=(0, 6))

        act = ttk.Frame(rel_box)
        act.pack(fill="x")
        ttk.Button(act, text="Tải lại bạn bè", command=self.load_friends).pack(side="left")
        ttk.Button(act, text="Chấp nhận lời mời", command=lambda: self._handle_respond_friend(True)).pack(side="left", padx=6)
        ttk.Button(act, text="Từ chối lời mời", command=lambda: self._handle_respond_friend(False)).pack(side="left")
        ttk.Button(act, text="Hủy kết bạn / Thu hồi", command=self._handle_remove_friend).pack(side="left", padx=6)

    def refresh_all(self) -> None:
        self._load_communities()
        if self._token():
            self.load_posts()
            self.load_friends()

    def _choose_attachment(self) -> None:
        path = filedialog.askopenfilename(title="Chọn tệp đính kèm minh họa")
        if path:
            self.post_attach_var.set(path)

    def _load_communities(self) -> None:
        base = self._server_url()

        def on_done(res):
            status, data = res
            if status != 200:
                return
            items = data.get("items", [])
            self._communities = items
            labels = [f"#{it['MaCongDong']} [{it['CapDo']}] {it['TenCongDong']}" for it in items]
            self.post_comm_cb["values"] = labels
            if labels and not self.post_comm_var.get():
                self.post_comm_cb.current(0)

        self._run_async(lambda: http_json(f"{base}/api/m02/communities/tree", "GET"), on_done)

    def _selected_community_id(self) -> int | None:
        idx = self.post_comm_cb.current()
        if 0 <= idx < len(self._communities):
            return int(self._communities[idx]["MaCongDong"])
        return None

    def _clear_post_form(self) -> None:
        self.post_edit_id.set("")
        self.post_attach_var.set("")
        self.post_text.delete("1.0", tk.END)

    def load_posts(self) -> None:
        tok = self._token()
        if not tok:
            self._set_status("Cần đăng nhập tài khoản trước khi xem bài viết.", True)
            return
        params = {}
        if self.p_search.get().strip():
            params["search"] = self.p_search.get().strip()
        qs = f"?{urllib.parse.urlencode(params)}" if params else ""
        url = f"{self._server_url()}/api/m03/posts{qs}"

        def on_done(res):
            status, data = res
            if status != 200:
                self._set_status(data.get("detail", f"Không tải được bài viết (HTTP {status})."), True)
                return
            for iid in self.posts_tree.get_children():
                self.posts_tree.delete(iid)
            self._posts_by_id.clear()
            for post in data.get("items", []):
                pid = int(post["MaBaiViet"])
                self._posts_by_id[pid] = post
                preview = (post.get("NoiDung") or "").replace("\n", " ")[:65]
                self.posts_tree.insert(
                    "",
                    "end",
                    iid=str(pid),
                    values=(
                        pid,
                        post.get("TenTacGia") or "",
                        post.get("TenCongDong") or "",
                        post.get("DanhMuc") or "",
                        post.get("SoLuotThich", 0),
                        post.get("SoBinhLuan", 0),
                        preview,
                    ),
                )
            self._set_status(f"Đã tải {len(data.get('items', []))} bài viết.", False)

        self._run_async(lambda: http_json(url, "GET", token=tok), on_done)

    def _on_select_post(self, _event=None) -> None:
        sel = self.posts_tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        self._selected_post_id = pid
        post = self._posts_by_id.get(pid)
        if not post:
            return
        self.post_edit_id.set(str(pid))
        self.post_cat_var.set(post.get("DanhMuc") or "HocTap")
        self.post_attach_var.set(post.get("TepDinhKem") or "")
        self.post_text.delete("1.0", tk.END)
        self.post_text.insert("1.0", post.get("NoiDung") or "")
        self.like_btn.config(text="Bỏ thích" if post.get("liked_by_me") else "Thích bài viết")
        self.post_meta_lbl.config(
            text=f"Bài #{pid} • {post.get('TenTacGia')} • Thích: {post.get('SoLuotThich', 0)} • Bình luận: {post.get('SoBinhLuan', 0)}"
        )
        self._load_comments(pid)

    def _load_comments(self, post_id: int) -> None:
        tok = self._token()
        if not tok:
            return
        url = f"{self._server_url()}/api/m03/posts/{post_id}/comments"

        def on_done(res):
            status, data = res
            if status != 200:
                return
            self.comments_list.delete(0, tk.END)
            for c in data.get("items", []):
                self.comments_list.insert(tk.END, f"[{c.get('TenNguoiBinhLuan')}] {c.get('NoiDung')}")

        self._run_async(lambda: http_json(url, "GET", token=tok), on_done)

    def _handle_create_post(self) -> None:
        tok = self._token()
        cid = self._selected_community_id()
        if not tok or not cid:
            self._set_status("Vui lòng đăng nhập và chọn Cộng đồng trước khi đăng bài.", True)
            return
        payload = {
            "cong_dong_id": cid,
            "danh_muc": self.post_cat_var.get(),
            "noi_dung": self.post_text.get("1.0", tk.END).strip(),
            "tep_dinh_kem": self.post_attach_var.get().strip() or None,
        }
        url = f"{self._server_url()}/api/m03/posts"

        def on_done(res):
            status, data = res
            if status == 201:
                self._set_status(data.get("message", "Đã đăng bài viết."), False)
                self._clear_post_form()
                self.load_posts()
            else:
                self._set_status(data.get("detail", f"Đăng bài thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "POST", payload, token=tok), on_done)

    def _handle_update_post(self) -> None:
        tok = self._token()
        pid = self.post_edit_id.get().strip()
        if not tok or not pid:
            self._set_status("Chọn bài viết cần chỉnh sửa.", True)
            return
        payload = {
            "danh_muc": self.post_cat_var.get(),
            "noi_dung": self.post_text.get("1.0", tk.END).strip(),
            "tep_dinh_kem": self.post_attach_var.get().strip() or None,
        }
        cid = self._selected_community_id()
        if cid is not None:
            payload["cong_dong_id"] = cid
        url = f"{self._server_url()}/api/m03/posts/{pid}"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Đã cập nhật bài viết."), False)
                self.load_posts()
            else:
                self._set_status(data.get("detail", f"Cập nhật thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "PUT", payload, token=tok), on_done)

    def _handle_delete_post(self) -> None:
        tok = self._token()
        pid = self.post_edit_id.get().strip()
        if not tok or not pid:
            self._set_status("Chọn bài viết cần xóa.", True)
            return
        if not messagebox.askyesno("Xác nhận", f"Xóa bài viết #{pid}?"):
            return
        url = f"{self._server_url()}/api/m03/posts/{pid}"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Đã xóa bài viết."), False)
                self._clear_post_form()
                self.load_posts()
            else:
                self._set_status(data.get("detail", f"Xóa bài thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "DELETE", token=tok), on_done)

    def _handle_toggle_like(self) -> None:
        tok = self._token()
        pid = self._selected_post_id
        if not tok or not pid:
            self._set_status("Chọn một bài viết trước khi bấm Thích.", True)
            return
        url = f"{self._server_url()}/api/m03/posts/{pid}/like"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Đã cập nhật tương tác."), False)
                self.load_posts()
            else:
                self._set_status(data.get("detail", f"Lỗi thao tác Thích (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "POST", {}, token=tok), on_done)

    def _handle_add_comment(self) -> None:
        tok = self._token()
        pid = self._selected_post_id
        text = self.comment_var.get().strip()
        if not tok or not pid or not text:
            self._set_status("Chọn bài viết và nhập nội dung bình luận.", True)
            return
        url = f"{self._server_url()}/api/m03/posts/{pid}/comments"

        def on_done(res):
            status, data = res
            if status == 201:
                self.comment_var.set("")
                self._load_comments(pid)
                self.load_posts()
                self._set_status("Đã gửi bình luận.", False)
            else:
                self._set_status(data.get("detail", f"Bình luận thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "POST", {"noi_dung": text}, token=tok), on_done)

    def search_students(self) -> None:
        tok = self._token()
        if not tok:
            self._set_status("Cần đăng nhập trước khi tìm bạn học.", True)
            return
        q = self.f_query.get().strip()
        qs = f"?{urllib.parse.urlencode({'q': q})}" if q else ""
        url = f"{self._server_url()}/api/m03/friends/search{qs}"

        def on_done(res):
            status, data = res
            if status != 200:
                self._set_status(data.get("detail", f"Tìm kiếm thất bại (HTTP {status})."), True)
                return
            for iid in self.search_tree.get_children():
                self.search_tree.delete(iid)
            self._search_users_by_id.clear()
            for u in data.get("items", []):
                uid = int(u["MaNguoiDung"])
                self._search_users_by_id[uid] = u
                self.search_tree.insert(
                    "",
                    "end",
                    iid=str(uid),
                    values=(uid, u.get("HoTen") or "", u.get("MaSinhVien") or "-", u.get("TenLop") or "-", u.get("QuanHe") or ""),
                )
            self._set_status(f"Tìm thấy {len(data.get('items', []))} bạn học.", False)

        self._run_async(lambda: http_json(url, "GET", token=tok), on_done)

    def load_friends(self) -> None:
        tok = self._token()
        if not tok:
            return
        url = f"{self._server_url()}/api/m03/friends"

        def on_done(res):
            status, data = res
            if status != 200:
                return
            for iid in self.rel_tree.get_children():
                self.rel_tree.delete(iid)
            groups = [
                ("Lời mời đến", data.get("incoming_requests", [])),
                ("Đã gửi", data.get("outgoing_requests", [])),
                ("Bạn bè", data.get("friends", [])),
            ]
            for label, rows in groups:
                for row in rows:
                    peer = row.get("peer", {})
                    self.rel_tree.insert(
                        "",
                        "end",
                        iid=str(row["MaKetBan"]),
                        values=(
                            row["MaKetBan"],
                            label,
                            peer.get("HoTen") or "",
                            peer.get("MaSinhVien") or "-",
                            peer.get("TenLop") or "-",
                            row.get("TrangThai") or "",
                        ),
                    )

        self._run_async(lambda: http_json(url, "GET", token=tok), on_done)

    def _handle_send_friend_request(self) -> None:
        tok = self._token()
        sel = self.search_tree.selection()
        if not tok or not sel:
            self._set_status("Chọn một sinh viên trong danh sách tìm kiếm để gửi lời mời.", True)
            return
        target_id = int(sel[0])
        url = f"{self._server_url()}/api/m03/friends/request"

        def on_done(res):
            status, data = res
            if status == 201:
                self._set_status(data.get("message", "Đã gửi lời mời kết bạn."), False)
                self.search_students()
                self.load_friends()
            else:
                self._set_status(data.get("detail", f"Gửi lời mời thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "POST", {"ma_nguoi_nhan": target_id}, token=tok), on_done)

    def _handle_respond_friend(self, accept: bool) -> None:
        tok = self._token()
        sel = self.rel_tree.selection()
        if not tok or not sel:
            self._set_status("Chọn một lời mời đến trong bảng bên dưới.", True)
            return
        fid = int(sel[0])
        url = f"{self._server_url()}/api/m03/friends/{fid}/respond"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Đã phản hồi lời mời."), False)
                self.load_friends()
                self.search_students()
            else:
                self._set_status(data.get("detail", f"Phản hồi thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "PUT", {"chap_nhan": accept}, token=tok), on_done)

    def _handle_remove_friend(self) -> None:
        tok = self._token()
        sel = self.rel_tree.selection()
        if not tok or not sel:
            self._set_status("Chọn một dòng kết bạn trong bảng để hủy.", True)
            return
        fid = int(sel[0])
        url = f"{self._server_url()}/api/m03/friends/{fid}"

        def on_done(res):
            status, data = res
            if status == 200:
                self._set_status(data.get("message", "Đã xóa quan hệ kết bạn."), False)
                self.load_friends()
                self.search_students()
            else:
                self._set_status(data.get("detail", f"Thao tác thất bại (HTTP {status})."), True)

        self._run_async(lambda: http_json(url, "DELETE", token=tok), on_done)
