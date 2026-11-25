"""FastAPI Controller cho M1: Tài khoản, Hồ sơ & Quên mật khẩu (OTP) (Nguyễn Ngô Tú Anh)."""
from fastapi import APIRouter
from ..Models import m01_model as model

router = APIRouter(prefix="/api/m01", tags=["M1 - Nguyễn Ngô Tú Anh"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["POST /api/m01/auth/register", "POST /api/m01/auth/login", "POST /api/m01/auth/logout", "PUT /api/m01/users/password", "POST /api/m01/auth/forgot-otp", "POST /api/m01/auth/reset-pw", "PUT /api/m01/users/profile"],
    }
