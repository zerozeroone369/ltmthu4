"""FastAPI Controller cho M10: Quản trị Hệ thống & Kiểm duyệt (Admin) (Nguyễn Ngô Tú Anh)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.Shared.middlewares.auth_middleware import require_admin, verify_token

from ..Models import m10_model as model
from ..Services import m10_service as service

router = APIRouter(prefix="/api/m10", tags=["M10 - Nguyễn Ngô Tú Anh"])

CurrentUser = Annotated[dict, Depends(verify_token)]
AdminUser = Annotated[dict, Depends(require_admin)]


class LockUserRequest(BaseModel):
    trang_thai: str | None = None
    locked: bool | None = None


class RoleUpdateRequest(BaseModel):
    vai_tro: str


class CreateReportRequest(BaseModel):
    loai_noi_dung: str = Field(..., max_length=30)
    id_noi_dung: int = Field(..., gt=0)
    ly_do: str = Field(..., min_length=1, max_length=100)
    chi_tiet: str | None = Field(default=None, max_length=1000)


class ModerateReportRequest(BaseModel):
    quyet_dinh: str
    ghi_chu_xu_ly: str | None = Field(default=None, max_length=500)


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": [
            "POST /api/m10/reports",
            "GET /api/m10/admin/users",
            "PUT /api/m10/admin/users/{id}/lock",
            "PUT /api/m10/admin/users/{id}/role",
            "GET /api/m10/admin/reports",
            "PUT /api/m10/admin/reports/{id}",
        ],
    }


@router.post("/reports", status_code=201)
def create_report(payload: CreateReportRequest, current_user: CurrentUser):
    return service.submit_report(
        reporter_id=current_user["user_id"],
        loai_noi_dung=payload.loai_noi_dung,
        id_noi_dung=payload.id_noi_dung,
        ly_do=payload.ly_do,
        chi_tiet=payload.chi_tiet,
    )


@router.get("/admin/users")
def admin_list_users(
    _admin: AdminUser,
    search: str = Query(default=""),
    vai_tro: str | None = Query(default=None),
    trang_thai: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return service.list_admin_users(
        search=search,
        vai_tro=vai_tro,
        trang_thai=trang_thai,
        limit=limit,
        offset=offset,
    )


@router.put("/admin/users/{user_id}/lock")
def admin_lock_user(
    user_id: int,
    payload: LockUserRequest,
    admin: AdminUser,
):
    target_status = payload.trang_thai
    if target_status is None and payload.locked is not None:
        target_status = "BiKhoa" if payload.locked else "HoatDong"
    if not target_status:
        raise HTTPException(status_code=400, detail="Cần truyền 'trang_thai' hoặc 'locked'.")
    return service.set_user_lock_status(
        admin_id=admin["user_id"],
        target_user_id=user_id,
        trang_thai=target_status,
    )


@router.put("/admin/users/{user_id}/role")
def admin_change_role(
    user_id: int,
    payload: RoleUpdateRequest,
    admin: AdminUser,
):
    return service.change_user_role(
        admin_id=admin["user_id"],
        target_user_id=user_id,
        vai_tro=payload.vai_tro,
    )


@router.get("/admin/reports")
def admin_list_reports(
    _admin: AdminUser,
    trang_thai: str | None = Query(default=None),
    loai_noi_dung: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return service.list_admin_reports(
        trang_thai=trang_thai,
        loai_noi_dung=loai_noi_dung,
        limit=limit,
        offset=offset,
    )


@router.put("/admin/reports/{report_id}")
def admin_moderate_report(
    report_id: int,
    payload: ModerateReportRequest,
    admin: AdminUser,
):
    return service.moderate_report(
        admin_id=admin["user_id"],
        report_id=report_id,
        quyet_dinh=payload.quyet_dinh,
        ghi_chu_xu_ly=payload.ghi_chu_xu_ly,
    )
