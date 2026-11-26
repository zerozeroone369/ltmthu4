"""Unit & API tests cho M02: Cây Cộng đồng 5 Cấp (Trường → Khoa → Ngành → Khóa → Lớp)."""
from __future__ import annotations

import tkinter as tk

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.Modules.M02_CongDong_5Cap__Duy.Controllers.m02_controller import router
from src.Modules.M02_CongDong_5Cap__Duy.Models import m02_model
from src.Modules.M02_CongDong_5Cap__Duy.Views.m02_view import Module02View
from src.Modules.M10_QuanTri_KiemDuyet__TuAnh.Views.m10_view import Module10View
from src.Shared.middlewares import auth_middleware


class FakeM02Repo:
    """In-memory repository simulating PostgreSQL CongDong 5-level tree."""

    def __init__(self) -> None:
        self.communities: dict[int, dict] = {
            1: {"MaCongDong": 1, "MaCongDongCha": None, "KyHieu": "CNTT-DEMO", "TenCongDong": "Đại học CNTT", "CapDo": "Truong", "NamBatDau": None, "TrangThai": "DangHoatDong"},
            2: {"MaCongDong": 2, "MaCongDongCha": 1, "KyHieu": "CNTT", "TenCongDong": "Khoa CNTT", "CapDo": "Khoa", "NamBatDau": None, "TrangThai": "DangHoatDong"},
            3: {"MaCongDong": 3, "MaCongDongCha": 2, "KyHieu": "MMT", "TenCongDong": "Ngành MMT", "CapDo": "Nganh", "NamBatDau": None, "TrangThai": "DangHoatDong"},
            4: {"MaCongDong": 4, "MaCongDongCha": 3, "KyHieu": "K2022", "TenCongDong": "Khóa 2022", "CapDo": "KhoaHoc", "NamBatDau": 2022, "TrangThai": "DangHoatDong"},
            5: {"MaCongDong": 5, "MaCongDongCha": 4, "KyHieu": "D22CQCN01", "TenCongDong": "Lớp D22CQCN01", "CapDo": "Lop", "NamBatDau": None, "TrangThai": "DangHoatDong"},
        }
        self.next_id = 6

    def get_community_by_id(self, community_id: int) -> dict | None:
        row = self.communities.get(community_id)
        return dict(row) if row else None

    def get_community_children(self, parent_id: int | None = None, include_inactive: bool = False) -> list[dict]:
        rows = [
            dict(c)
            for c in self.communities.values()
            if c["MaCongDongCha"] == parent_id and (include_inactive or c["TrangThai"] == "DangHoatDong")
        ]
        return sorted(rows, key=lambda r: r["TenCongDong"])

    def list_communities(
        self,
        *,
        cap_do: str | None = None,
        trang_thai: str | None = None,
        parent_id: int | None = None,
        search: str = "",
        include_inactive: bool = True,
    ) -> list[dict]:
        rows = list(self.communities.values())
        if cap_do:
            rows = [r for r in rows if r["CapDo"] == cap_do]
        if trang_thai:
            rows = [r for r in rows if r["TrangThai"] == trang_thai]
        elif not include_inactive:
            rows = [r for r in rows if r["TrangThai"] == "DangHoatDong"]
        if parent_id is not None:
            rows = [r for r in rows if r["MaCongDongCha"] == parent_id]
        if search.strip():
            q = search.strip().lower()
            rows = [r for r in rows if q in r["TenCongDong"].lower() or q in (r.get("KyHieu") or "").lower()]
        rows.sort(key=lambda r: (r["MaCongDongCha"] or 0, r["TenCongDong"], r["MaCongDong"]))
        return [dict(r) for r in rows]

    def get_community_chain(self, community_id: int) -> list[dict]:
        chain: list[dict] = []
        cur = self.communities.get(community_id)
        while cur:
            chain.append(dict(cur))
            pid = cur.get("MaCongDongCha")
            cur = self.communities.get(pid) if pid else None
        chain.reverse()
        return chain

    def get_descendant_ids(self, community_id: int, include_inactive: bool = False) -> list[int]:
        if community_id not in self.communities:
            return []
        result = [community_id]
        queue = [community_id]
        while queue:
            pid = queue.pop(0)
            for cid, row in self.communities.items():
                if row["MaCongDongCha"] == pid and (include_inactive or row["TrangThai"] == "DangHoatDong"):
                    result.append(cid)
                    queue.append(cid)
        return sorted(result)

    def find_duplicate_code(
        self,
        ky_hieu: str,
        parent_id: int | None,
        cap_do: str,
        exclude_id: int | None = None,
    ) -> dict | None:
        target = ky_hieu.lower()
        for row in self.communities.values():
            if exclude_id is not None and row["MaCongDong"] == exclude_id:
                continue
            if (
                (row.get("KyHieu") or "").lower() == target
                and row["CapDo"] == cap_do
                and row["MaCongDongCha"] == parent_id
            ):
                return dict(row)
        return None

    def count_active_children(self, community_id: int) -> int:
        return sum(
            1
            for row in self.communities.values()
            if row["MaCongDongCha"] == community_id and row["TrangThai"] == "DangHoatDong"
        )

    def create_community(self, data: dict) -> dict:
        cid = self.next_id
        self.next_id += 1
        row = {
            "MaCongDong": cid,
            "MaCongDongCha": data.get("MaCongDongCha"),
            "KyHieu": data.get("KyHieu"),
            "TenCongDong": data["TenCongDong"],
            "CapDo": data["CapDo"],
            "NamBatDau": data.get("NamBatDau"),
            "TrangThai": data.get("TrangThai", "DangHoatDong"),
        }
        self.communities[cid] = row
        return dict(row)

    def update_community(self, community_id: int, fields: dict) -> dict | None:
        row = self.communities.get(community_id)
        if not row:
            return None
        row.update(fields)
        return dict(row)

    def deactivate_community(self, community_id: int, cascade: bool = False) -> list[dict]:
        ids = self.get_descendant_ids(community_id, include_inactive=True) if cascade else [community_id]
        affected: list[dict] = []
        for cid in ids:
            row = self.communities.get(cid)
            if row:
                row["TrangThai"] = "NgungHoatDong"
                affected.append(dict(row))
        return affected


@pytest.fixture()
def m02_env(monkeypatch):
    repo = FakeM02Repo()
    users = {
        1: {"MaNguoiDung": 1, "TrangThai": "HoatDong", "VaiTro": "QuanTriVien", "Email": "admin@dau.edu.vn", "HoTen": "Admin", "MaLop": 5},
        2: {"MaNguoiDung": 2, "TrangThai": "HoatDong", "VaiTro": "SinhVien", "Email": "duy@dau.edu.vn", "HoTen": "Duy", "MaLop": 5},
    }
    monkeypatch.setattr(auth_middleware, "get_jwt_secret", lambda: "test-m02-secret-key-at-least-32b")
    monkeypatch.setattr(auth_middleware, "fetch_active_user_auth_state", lambda uid: users.get(uid))
    auth_middleware.clear_revoked_tokens()

    for attr in (
        "get_community_by_id",
        "get_community_children",
        "list_communities",
        "get_community_chain",
        "get_descendant_ids",
        "find_duplicate_code",
        "count_active_children",
        "create_community",
        "update_community",
        "deactivate_community",
    ):
        monkeypatch.setattr(m02_model, attr, getattr(repo, attr))

    app = FastAPI()
    app.include_router(router)
    admin_tok, _ = auth_middleware.create_access_token(1, "admin@dau.edu.vn", "QuanTriVien")
    sv_tok, _ = auth_middleware.create_access_token(2, "duy@dau.edu.vn", "SinhVien")
    return TestClient(app), repo, admin_tok, sv_tok


def test_cascading_queries_chain_and_tree(m02_env):
    client, _, _, _ = m02_env

    roots = client.get("/api/m02/communities/roots")
    assert roots.status_code == 200
    assert len(roots.json()["items"]) == 1
    assert roots.json()["items"][0]["KyHieu"] == "CNTT-DEMO"

    children = client.get("/api/m02/communities/1/children")
    assert children.status_code == 200
    assert children.json()["items"][0]["CapDo"] == "Khoa"

    assert client.get("/api/m02/communities/999/children").status_code == 404

    chain = client.get("/api/m02/communities/chain/5")
    assert chain.status_code == 200
    caps = [item["CapDo"] for item in chain.json()["chain"]]
    assert caps == ["Truong", "Khoa", "Nganh", "KhoaHoc", "Lop"]

    tree = client.get("/api/m02/communities/tree")
    assert tree.status_code == 200
    assert tree.json()["tree"][0]["children"][0]["children"][0]["children"][0]["children"][0]["KyHieu"] == "D22CQCN01"

    desc = client.get("/api/m02/communities/2/descendants")
    assert desc.status_code == 200
    assert desc.json()["descendant_ids"] == [2, 3, 4, 5]


def test_admin_community_crud_hierarchy_and_cascade_deactivate(m02_env):
    client, _, admin_tok, sv_tok = m02_env
    admin_headers = {"Authorization": f"Bearer {admin_tok}"}
    sv_headers = {"Authorization": f"Bearer {sv_tok}"}

    # Non-admin blocked
    assert client.get("/api/m02/admin/communities", headers=sv_headers).status_code == 403
    assert (
        client.post(
            "/api/m02/admin/communities",
            headers=sv_headers,
            json={"cap_do": "Lop", "ma_cong_dong_cha": 4, "ten_cong_dong": "Lớp X"},
        ).status_code
        == 403
    )

    # Wrong parent level rejected (Lop cannot attach directly under Khoa)
    bad_level = client.post(
        "/api/m02/admin/communities",
        headers=admin_headers,
        json={"cap_do": "Lop", "ma_cong_dong_cha": 2, "ky_hieu": "ERR", "ten_cong_dong": "Sai cấp"},
    )
    assert bad_level.status_code == 400

    # Valid new Lop created and immediately available in cascade
    ok_cls = client.post(
        "/api/m02/admin/communities",
        headers=admin_headers,
        json={"cap_do": "Lop", "ma_cong_dong_cha": 4, "ky_hieu": "D22CQCN02", "ten_cong_dong": "Lớp D22CQCN02"},
    )
    assert ok_cls.status_code == 201, ok_cls.text
    new_lop_id = ok_cls.json()["community"]["MaCongDong"]

    # Duplicate sibling KyHieu rejected
    dup_cls = client.post(
        "/api/m02/admin/communities",
        headers=admin_headers,
        json={"cap_do": "Lop", "ma_cong_dong_cha": 4, "ky_hieu": "d22cqcn02", "ten_cong_dong": "Trùng"},
    )
    assert dup_cls.status_code == 409

    # Update name succeeds
    upd = client.put(
        f"/api/m02/admin/communities/{new_lop_id}",
        headers=admin_headers,
        json={"ten_cong_dong": "Lớp D22CQCN02 - Chất lượng cao"},
    )
    assert upd.status_code == 200
    assert "Chất lượng cao" in upd.json()["community"]["TenCongDong"]

    # Deactivating KhoaHoc #4 without cascade rejected because it has active children
    no_cascade = client.delete("/api/m02/admin/communities/4", headers=admin_headers)
    assert no_cascade.status_code == 400

    # Cascade deactivation disables KhoaHoc #4 and its Lop children
    cascade_res = client.delete("/api/m02/admin/communities/4?cascade=true", headers=admin_headers)
    assert cascade_res.status_code == 200
    assert cascade_res.json()["affected_count"] == 3

    # Inactive KhoaHoc no longer appears in public children of Nganh #3
    public_children = client.get("/api/m02/communities/3/children").json()["items"]
    assert public_children == []

    # Cannot reactivate child while parent is still NgungHoatDong
    reactivate_child = client.put(
        f"/api/m02/admin/communities/{new_lop_id}",
        headers=admin_headers,
        json={"trang_thai": "DangHoatDong"},
    )
    assert reactivate_child.status_code == 400


def test_module02_tkinter_and_m10_embedding_smoke():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No GUI display available")
    root.withdraw()

    m10 = Module10View(root, server_url="http://127.0.0.1:8000", get_token=lambda: "inherited-admin-jwt")
    m02_standalone = Module02View(root, server_url="http://127.0.0.1:8000")
    embedded = [w for w in m10.m02_tab.winfo_children() if isinstance(w, Module02View)]
    assert len(embedded) == 1
    assert embedded[0]._token() == "inherited-admin-jwt"
    assert len(m02_standalone.notebook.tabs()) == 2
    root.update_idletasks()
    root.destroy()


def test_update_prevents_cycle_and_invalid_move(m02_env):
    client, _, admin_tok, _ = m02_env
    admin_headers = {"Authorization": f"Bearer {admin_tok}"}

    # Cannot attach Khoa #2 to itself or change Truong #1 parent
    assert (
        client.put(
            "/api/m02/admin/communities/2",
            headers=admin_headers,
            json={"ma_cong_dong_cha": 2},
        ).status_code
        == 400
    )
    assert (
        client.put(
            "/api/m02/admin/communities/1",
            headers=admin_headers,
            json={"ma_cong_dong_cha": 2},
        ).status_code
        == 400
    )
