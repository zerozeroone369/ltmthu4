"""FastAPI Controller cho M8: Khung Tkinter Chung, Bảng tin & Riêng tư (Thái)."""
from fastapi import APIRouter
from ..Models import m08_model as model

router = APIRouter(prefix="/api/m08", tags=["M8 - Thái"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["GET /api/m08/feed", "PUT /api/m08/privacy", "POST /api/m08/block/{targetId}", "DELETE /api/m08/block/{targetId}"],
    }
