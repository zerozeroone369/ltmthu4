"""FastAPI Controller cho M5: Hỏi đáp Học thuật (Q&A & Upvote) (Huy)."""
from fastapi import APIRouter
from ..Models import m05_model as model

router = APIRouter(prefix="/api/m05", tags=["M5 - Huy"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["CRUD /api/m05/questions", "POST /api/m05/questions/{id}/answers", "POST /api/m05/answers/{id}/upvote", "PUT /api/m05/answers/{id}/correct"],
    }
