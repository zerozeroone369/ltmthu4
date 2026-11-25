"""FastAPI Controller cho M1: Tài khoản, Hồ sơ & Quên mật khẩu (OTP) (Nguyễn Ngô Tú Anh)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.Shared.middlewares.auth_middleware import verify_token

from ..Models import m01_model as model
from ..Services import m01_service as service

router = APIRouter(prefix="/api/m01", tags=["M1 - Nguyễn Ngô Tú Anh"])

CurrentUser = Annotated[dict, Depends(verify_token)]


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=6, max_length=72)
    ho_ten: str = Field(..., min_length=1, max_length=100)
    ma_lop: int | None = None
    ma_sinh_vien: str | None = Field(default=None, max_length=30)
    so_dien_thoai: str | None = Field(default=None, max_length=20)
    gioi_thieu: str | None = Field(default=None, max_length=500)


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=1, max_length=72)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1, max_length=72)
    new_password: str = Field(..., min_length=6, max_length=72)


class ForgotOtpRequest(BaseModel):
    email: str = Field(..., max_length=254)


class ResetPasswordRequest(BaseModel):
    email: str = Field(..., max_length=254)
    otp: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6, max_length=72)


class ProfileUpdateRequest(BaseModel):
    ho_ten: str | None = Field(default=None, max_length=100)
    so_dien_thoai: str | None = Field(default=None, max_length=20)
    anh_dai_dien: str | None = Field(default=None, max_length=255)
    gioi_thieu: str | None = Field(default=None, max_length=500)
    ma_sinh_vien: str | None = Field(default=None, max_length=30)
    ma_lop: int | None = None
    cai_dat_rieng_tu: dict[str, str] | None = None


class PrivacyUpdateRequest(BaseModel):
    cai_dat_rieng_tu: dict[str, str]


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": [
            "GET /api/m01/communities/children",
            "GET /api/m01/communities/chain/{lop_id}",
            "POST /api/m01/auth/register",
            "POST /api/m01/auth/login",
            "POST /api/m01/auth/logout",
            "GET /api/m01/users/me",
            "PUT /api/m01/users/password",
            "POST /api/m01/auth/forgot-otp",
            "POST /api/m01/auth/reset-pw",
            "PUT /api/m01/users/profile",
            "PUT /api/m01/users/privacy",
        ],
    }


@router.get("/communities/children")
def list_communities(parent_id: int | None = Query(default=None)):
    items = service.list_community_children(parent_id)
    return {"ok": True, "items": items}


@router.get("/communities/chain/{lop_id}")
def get_community_chain(lop_id: int):
    chain = service.fetch_community_chain(lop_id)
    return {"ok": True, "chain": chain}


@router.post("/auth/register", status_code=201)
def register(payload: RegisterRequest):
    return service.register_student(
        email=payload.email,
        password=payload.password,
        ho_ten=payload.ho_ten,
        ma_lop=payload.ma_lop,
        ma_sinh_vien=payload.ma_sinh_vien,
        so_dien_thoai=payload.so_dien_thoai,
        gioi_thieu=payload.gioi_thieu,
    )


@router.post("/auth/login")
def login(payload: LoginRequest):
    return service.login_user(email=payload.email, password=payload.password)


@router.post("/auth/logout")
def logout(current_user: CurrentUser):
    return service.logout_user(current_user)


@router.get("/users/me")
def get_me(current_user: CurrentUser):
    return service.get_my_profile(current_user["user_id"])


@router.put("/users/password")
def change_password(payload: ChangePasswordRequest, current_user: CurrentUser):
    return service.change_password(
        user_id=current_user["user_id"],
        old_password=payload.old_password,
        new_password=payload.new_password,
    )


@router.post("/auth/forgot-otp")
def forgot_otp(payload: ForgotOtpRequest):
    return service.request_forgot_otp(email=payload.email)


@router.post("/auth/reset-pw")
def reset_password(payload: ResetPasswordRequest):
    return service.reset_password_with_otp(
        email=payload.email,
        otp=payload.otp,
        new_password=payload.new_password,
    )


@router.put("/users/profile")
def update_profile(payload: ProfileUpdateRequest, current_user: CurrentUser):
    return service.update_profile_and_privacy(
        user_id=current_user["user_id"],
        ho_ten=payload.ho_ten,
        so_dien_thoai=payload.so_dien_thoai,
        anh_dai_dien=payload.anh_dai_dien,
        gioi_thieu=payload.gioi_thieu,
        ma_sinh_vien=payload.ma_sinh_vien,
        ma_lop=payload.ma_lop,
        cai_dat_rieng_tu=payload.cai_dat_rieng_tu,
    )


@router.put("/users/privacy")
def update_privacy(payload: PrivacyUpdateRequest, current_user: CurrentUser):
    return service.update_profile_and_privacy(
        user_id=current_user["user_id"],
        cai_dat_rieng_tu=payload.cai_dat_rieng_tu,
    )
