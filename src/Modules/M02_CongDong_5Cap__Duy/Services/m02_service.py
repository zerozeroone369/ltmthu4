"""Business logic cho M2: Cây Cộng đồng 5 Cấp (Trường → Khoa → Ngành → Khóa → Lớp) (Duy)."""
from __future__ import annotations

from fastapi import HTTPException

from ..Models import m02_model as model

LEVEL_ORDER = ("Truong", "Khoa", "Nganh", "KhoaHoc", "Lop")
EXPECTED_PARENT_LEVEL: dict[str, str | None] = {
    "Truong": None,
    "Khoa": "Truong",
    "Nganh": "Khoa",
    "KhoaHoc": "Nganh",
    "Lop": "KhoaHoc",
}
VALID_STATUSES = {"DangHoatDong", "NgungHoatDong"}


def _clean_optional_code(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if len(cleaned) > 30:
        raise HTTPException(status_code=400, detail="Ký hiệu cộng đồng tối đa 30 ký tự.")
    return cleaned


def _clean_name(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Tên cộng đồng không được để trống.")
    if len(cleaned) > 200:
        raise HTTPException(status_code=400, detail="Tên cộng đồng tối đa 200 ký tự.")
    return cleaned


def _validate_level_and_parent(
    *,
    cap_do: str,
    parent_id: int | None,
    self_id: int | None = None,
    require_active_parent: bool = True,
) -> None:
    if cap_do not in EXPECTED_PARENT_LEVEL:
        raise HTTPException(
            status_code=400,
            detail=f"CapDo không hợp lệ. Phải thuộc {list(LEVEL_ORDER)}.",
        )
    expected_parent_cap = EXPECTED_PARENT_LEVEL[cap_do]
    if expected_parent_cap is None:
        if parent_id is not None:
            raise HTTPException(status_code=400, detail="Cấp Trường không được có đơn vị cha.")
        return

    if parent_id is None:
        raise HTTPException(
            status_code=400,
            detail=f"Cấp '{cap_do}' bắt buộc phải chọn đơn vị cha thuộc cấp '{expected_parent_cap}'.",
        )
    if self_id is not None and int(parent_id) == int(self_id):
        raise HTTPException(status_code=400, detail="Không thể chọn chính đơn vị này làm đơn vị cha.")

    parent = model.get_community_by_id(parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị cha trong cây cộng đồng.")
    if parent["CapDo"] != expected_parent_cap:
        raise HTTPException(
            status_code=400,
            detail=f"Cấp '{cap_do}' phải trực thuộc cấp '{expected_parent_cap}', không thể gắn dưới '{parent['CapDo']}'.",
        )
    if require_active_parent and parent["TrangThai"] != "DangHoatDong":
        raise HTTPException(status_code=400, detail="Đơn vị cha đang tạm ngưng hoạt động.")

    if self_id is not None:
        descendants = set(model.get_descendant_ids(self_id, include_inactive=True))
        if int(parent_id) in descendants:
            raise HTTPException(status_code=400, detail="Không thể di chuyển đơn vị vào nhánh con của chính nó.")


def build_tree_hierarchy(items: list[dict]) -> list[dict]:
    """Convert flat CongDong rows into nested children trees ordered root-to-leaf."""
    nodes: dict[int, dict] = {}
    roots: list[dict] = []

    for item in items:
        node = dict(item)
        node["children"] = []
        nodes[int(node["MaCongDong"])] = node

    for node in nodes.values():
        parent_id = node.get("MaCongDongCha")
        if parent_id is not None and int(parent_id) in nodes:
            nodes[int(parent_id)]["children"].append(node)
        else:
            roots.append(node)
    return roots


def list_roots(include_inactive: bool = False) -> list[dict]:
    return model.get_community_children(parent_id=None, include_inactive=include_inactive)


def list_children(parent_id: int, include_inactive: bool = False) -> dict:
    parent = model.get_community_by_id(parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Không tìm thấy cộng đồng cha.")
    items = model.get_community_children(parent_id=parent_id, include_inactive=include_inactive)
    return {"parent": parent, "items": items}


def get_community_chain(community_id: int) -> dict:
    chain = model.get_community_chain(community_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Không tìm thấy cộng đồng trong cây 5 cấp.")
    levels = {item["CapDo"]: item for item in chain}
    return {"chain": chain, "levels": levels}


def get_community_tree(include_inactive: bool = False) -> dict:
    items = model.list_communities(include_inactive=include_inactive)
    return {"items": items, "tree": build_tree_hierarchy(items)}


def get_community_descendants(community_id: int, include_inactive: bool = False) -> dict:
    target = model.get_community_by_id(community_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy cộng đồng.")
    ids = model.get_descendant_ids(community_id, include_inactive=include_inactive)
    return {"community": target, "descendant_ids": ids}


def admin_list_communities(
    *,
    cap_do: str | None = None,
    trang_thai: str | None = None,
    parent_id: int | None = None,
    search: str = "",
) -> dict:
    if cap_do and cap_do not in EXPECTED_PARENT_LEVEL:
        raise HTTPException(status_code=400, detail="Cấp độ lọc không hợp lệ.")
    if trang_thai and trang_thai not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Trạng thái lọc không hợp lệ.")

    items = model.list_communities(
        cap_do=cap_do,
        trang_thai=trang_thai,
        parent_id=parent_id,
        search=search,
        include_inactive=True,
    )
    return {"items": items, "total": len(items)}


def admin_create_community(
    *,
    cap_do: str,
    ten_cong_dong: str,
    ma_cong_dong_cha: int | None = None,
    ky_hieu: str | None = None,
    nam_bat_dau: int | None = None,
) -> dict:
    name = _clean_name(ten_cong_dong)
    code = _clean_optional_code(ky_hieu)

    if nam_bat_dau is not None and (nam_bat_dau < 1950 or nam_bat_dau > 2100):
        raise HTTPException(status_code=400, detail="Năm bắt đầu phải nằm trong khoảng 1950–2100.")
    if cap_do != "KhoaHoc" and nam_bat_dau is not None:
        nam_bat_dau = None

    _validate_level_and_parent(
        cap_do=cap_do,
        parent_id=ma_cong_dong_cha,
        require_active_parent=True,
    )

    if code and model.find_duplicate_code(code, ma_cong_dong_cha, cap_do):
        raise HTTPException(status_code=409, detail=f"Ký hiệu '{code}' đã tồn tại trong cùng cấp và đơn vị cha.")

    try:
        created = model.create_community(
            {
                "MaCongDongCha": ma_cong_dong_cha,
                "KyHieu": code,
                "TenCongDong": name,
                "CapDo": cap_do,
                "NamBatDau": nam_bat_dau,
                "TrangThai": "DangHoatDong",
            }
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Không thể tạo cộng đồng: {exc}") from exc

    return {"ok": True, "message": f"Đã tạo {cap_do} '{name}'.", "community": created}


def admin_update_community(
    community_id: int,
    *,
    ten_cong_dong: str | None = None,
    ky_hieu: str | None = None,
    ma_cong_dong_cha: int | None = None,
    ma_cong_dong_cha_provided: bool = False,
    nam_bat_dau: int | None = None,
    trang_thai: str | None = None,
) -> dict:
    existing = model.get_community_by_id(community_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị cộng đồng.")

    fields: dict[str, object] = {}
    cap_do = existing["CapDo"]
    next_parent_id = ma_cong_dong_cha if ma_cong_dong_cha_provided else existing["MaCongDongCha"]

    if ma_cong_dong_cha_provided:
        _validate_level_and_parent(
            cap_do=cap_do,
            parent_id=next_parent_id,
            self_id=community_id,
            require_active_parent=(trang_thai or existing["TrangThai"]) == "DangHoatDong",
        )
        fields["MaCongDongCha"] = next_parent_id

    if ten_cong_dong is not None:
        fields["TenCongDong"] = _clean_name(ten_cong_dong)

    if ky_hieu is not None:
        code = _clean_optional_code(ky_hieu)
        if code and model.find_duplicate_code(code, next_parent_id, cap_do, exclude_id=community_id):
            raise HTTPException(status_code=409, detail=f"Ký hiệu '{code}' đã tồn tại ở đơn vị cùng cấp.")
        fields["KyHieu"] = code

    if nam_bat_dau is not None:
        if nam_bat_dau < 1950 or nam_bat_dau > 2100:
            raise HTTPException(status_code=400, detail="Năm bắt đầu phải nằm trong khoảng 1950–2100.")
        fields["NamBatDau"] = nam_bat_dau if cap_do == "KhoaHoc" else None

    if trang_thai is not None:
        if trang_thai not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Trạng thái phải là 'DangHoatDong' hoặc 'NgungHoatDong'.")
        if trang_thai == "DangHoatDong" and next_parent_id is not None:
            parent = model.get_community_by_id(int(next_parent_id))
            if not parent or parent["TrangThai"] != "DangHoatDong":
                raise HTTPException(status_code=400, detail="Không thể kích hoạt lại khi đơn vị cha đang tạm ngưng.")
        if trang_thai == "NgungHoatDong" and model.count_active_children(community_id) > 0:
            raise HTTPException(
                status_code=400,
                detail="Đơn vị này vẫn còn đơn vị con đang hoạt động; hãy tạm ngưng các cấp con trước.",
            )
        fields["TrangThai"] = trang_thai

    updated = model.update_community(community_id, fields)
    return {"ok": True, "message": "Đã cập nhật đơn vị cộng đồng.", "community": updated}


def admin_deactivate_community(community_id: int, cascade: bool = False) -> dict:
    existing = model.get_community_by_id(community_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị cộng đồng.")

    if not cascade and model.count_active_children(community_id) > 0:
        raise HTTPException(
            status_code=400,
            detail="Đơn vị còn cấp con đang hoạt động. Truyền cascade=true để tạm ngưng toàn nhánh.",
        )

    affected = model.deactivate_community(community_id, cascade=cascade)
    primary = next((item for item in affected if int(item["MaCongDong"]) == community_id), affected[0] if affected else existing)
    return {
        "ok": True,
        "message": f"Đã tạm ngưng {len(affected)} đơn vị cộng đồng.",
        "community": primary,
        "affected_count": len(affected),
    }
