"""FastAPI Controller cho M3: Bài viết, Tương tác & Kết bạn (Duy)."""
from fastapi import APIRouter
from ..Models import m03_model as model

router = APIRouter(prefix="/api/m03", tags=["M3 - Duy"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["CRUD /api/m03/posts", "POST /api/m03/posts/{id}/comments", "POST /api/m03/posts/{id}/like", "POST /api/m03/friends/request", "PUT /api/m03/friends/{id}/respond"],
    }
