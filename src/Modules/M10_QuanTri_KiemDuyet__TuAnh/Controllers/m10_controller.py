"""FastAPI Controller cho M10: Quản trị Hệ thống & Kiểm duyệt (Admin) (Nguyễn Ngô Tú Anh)."""
from fastapi import APIRouter
from ..Models import m10_model as model

router = APIRouter(prefix="/api/m10", tags=["M10 - Nguyễn Ngô Tú Anh"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["GET /api/m10/admin/users", "PUT /api/m10/admin/users/{id}/lock", "PUT /api/m10/admin/users/{id}/role", "GET /api/m10/admin/reports", "PUT /api/m10/admin/reports/{id}"],
    }
