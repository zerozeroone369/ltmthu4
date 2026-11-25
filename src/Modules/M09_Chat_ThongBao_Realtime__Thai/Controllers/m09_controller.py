"""FastAPI Controller cho M9: Nhắn tin Realtime & Thông báo (Thái)."""
from fastapi import APIRouter
from ..Models import m09_model as model

router = APIRouter(prefix="/api/m09", tags=["M9 - Thái"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["GET /api/m09/chat/history", "POST /api/m09/chat/send", "GET /api/m09/notifications", "PUT /api/m09/notifications/{id}/read", "WS /ws (chat_message, notification)"],
    }
