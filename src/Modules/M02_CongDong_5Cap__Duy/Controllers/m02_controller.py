"""FastAPI Controller cho M2: Cây Cộng đồng 5 Cấp (Trường → Lớp) (Duy)."""
from fastapi import APIRouter
from ..Models import m02_model as model

router = APIRouter(prefix="/api/m02", tags=["M2 - Duy"])


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": ["GET /api/m02/communities/roots", "GET /api/m02/communities/{parentId}/children", "GET /api/m02/communities/chain/{lopId}", "CRUD /api/m02/admin/communities"],
    }
