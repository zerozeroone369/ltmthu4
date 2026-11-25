"""FastAPI Controller cho M7: Campus (Tin tức, Học bổng, Sự kiện) (Bảo)."""
from fastapi import APIRouter
from ..Models import m07_model as model

router = APIRouter(prefix="/api/m07", tags=["M7 - Bảo"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["GET /api/m07/campus", "POST /api/m07/admin/campus", "PUT /api/m07/admin/campus/{id}", "DELETE /api/m07/admin/campus/{id}"],
    }
