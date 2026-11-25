"""FastAPI Controller cho M4: Tài liệu Học tập & Truyền tệp (Huy)."""
from fastapi import APIRouter
from ..Models import m04_model as model

router = APIRouter(prefix="/api/m04", tags=["M4 - Huy"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["GET /api/m04/subjects", "POST /api/m04/documents/upload", "GET /api/m04/documents/search", "GET /api/m04/documents/{id}/download", "POST /api/m04/documents/{id}/rate"],
    }
