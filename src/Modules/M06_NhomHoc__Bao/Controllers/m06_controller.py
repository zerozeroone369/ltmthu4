"""FastAPI Controller cho M6: Nhóm học Tập (Study Groups) (Bảo)."""
from fastapi import APIRouter
from ..Models import m06_model as model

router = APIRouter(prefix="/api/m06", tags=["M6 - Bảo"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["POST /api/m06/groups", "GET /api/m06/groups/search", "POST /api/m06/groups/{id}/join", "PUT /api/m06/groups/{id}/requests/{uid}", "PUT /api/m06/groups/{id}/capacity", "POST /api/m06/groups/{id}/transfer-leave"],
    }
