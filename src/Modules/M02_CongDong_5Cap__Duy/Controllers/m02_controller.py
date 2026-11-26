"""FastAPI Controller cho M2: Cây Cộng đồng 5 Cấp (Trường → Lớp) (Duy)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.Shared.middlewares.auth_middleware import require_admin

from ..Models import m02_model as model
from ..Services import m02_service as service

router = APIRouter(prefix="/api/m02", tags=["M2 - Duy"])

AdminUser = Annotated[dict, Depends(require_admin)]


class CommunityCreateRequest(BaseModel):
    cap_do: str = Field(..., max_length=20)
    ten_cong_dong: str = Field(..., min_length=1, max_length=200)
    ma_cong_dong_cha: int | None = None
    ky_hieu: str | None = Field(default=None, max_length=30)
    nam_bat_dau: int | None = None


class CommunityUpdateRequest(BaseModel):
    ten_cong_dong: str | None = Field(default=None, max_length=200)
    ky_hieu: str | None = Field(default=None, max_length=30)
    ma_cong_dong_cha: int | None = None
    nam_bat_dau: int | None = None
    trang_thai: str | None = Field(default=None, max_length=20)


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": [
            "GET /api/m02/communities/roots",
            "GET /api/m02/communities/{parentId}/children",
            "GET /api/m02/communities/chain/{lopId}",
            "GET /api/m02/communities/tree",
            "GET /api/m02/communities/{communityId}/descendants",
            "GET /api/m02/admin/communities",
            "POST /api/m02/admin/communities",
            "PUT /api/m02/admin/communities/{id}",
            "DELETE /api/m02/admin/communities/{id}",
        ],
    }


@router.get("/communities/roots")
def list_root_communities(include_inactive: bool = Query(default=False)):
    items = service.list_roots(include_inactive=include_inactive)
    return {"ok": True, "items": items}


@router.get("/communities/tree")
def get_community_tree(include_inactive: bool = Query(default=False)):
    data = service.get_community_tree(include_inactive=include_inactive)
    return {"ok": True, **data}


@router.get("/communities/chain/{lop_id}")
def get_community_chain(lop_id: int):
    data = service.get_community_chain(lop_id)
    return {"ok": True, **data}


@router.get("/communities/{parent_id}/children")
def list_child_communities(parent_id: int, include_inactive: bool = Query(default=False)):
    data = service.list_children(parent_id=parent_id, include_inactive=include_inactive)
    return {"ok": True, **data}


@router.get("/communities/{community_id}/descendants")
def get_community_descendants(community_id: int, include_inactive: bool = Query(default=False)):
    data = service.get_community_descendants(community_id, include_inactive=include_inactive)
    return {"ok": True, **data}


@router.get("/admin/communities")
def admin_list_communities(
    _admin: AdminUser,
    cap_do: str | None = Query(default=None),
    trang_thai: str | None = Query(default=None),
    parent_id: int | None = Query(default=None),
    search: str = Query(default=""),
):
    data = service.admin_list_communities(
        cap_do=cap_do,
        trang_thai=trang_thai,
        parent_id=parent_id,
        search=search,
    )
    return {"ok": True, **data}


@router.post("/admin/communities", status_code=201)
def admin_create_community(payload: CommunityCreateRequest, _admin: AdminUser):
    return service.admin_create_community(
        cap_do=payload.cap_do,
        ten_cong_dong=payload.ten_cong_dong,
        ma_cong_dong_cha=payload.ma_cong_dong_cha,
        ky_hieu=payload.ky_hieu,
        nam_bat_dau=payload.nam_bat_dau,
    )


@router.put("/admin/communities/{community_id}")
def admin_update_community(
    community_id: int,
    payload: CommunityUpdateRequest,
    _admin: AdminUser,
):
    return service.admin_update_community(
        community_id,
        ten_cong_dong=payload.ten_cong_dong,
        ky_hieu=payload.ky_hieu,
        ma_cong_dong_cha=payload.ma_cong_dong_cha,
        ma_cong_dong_cha_provided="ma_cong_dong_cha" in payload.model_fields_set,
        nam_bat_dau=payload.nam_bat_dau,
        trang_thai=payload.trang_thai,
    )


@router.delete("/admin/communities/{community_id}")
def admin_delete_community(
    community_id: int,
    _admin: AdminUser,
    cascade: bool = Query(default=False),
):
    return service.admin_deactivate_community(community_id, cascade=cascade)
