"""FastAPI Controller cho M3: Bài viết, Tương tác & Kết bạn (Duy)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.Shared.middlewares.auth_middleware import verify_token

from ..Models import m03_model as model
from ..Services import m03_service as service

router = APIRouter(prefix="/api/m03", tags=["M3 - Duy"])

CurrentUser = Annotated[dict, Depends(verify_token)]


class PostCreateRequest(BaseModel):
    cong_dong_id: int = Field(..., gt=0)
    noi_dung: str = Field(..., min_length=1)
    danh_muc: str = Field(default="HocTap", max_length=30)
    tep_dinh_kem: str | None = Field(default=None, max_length=500)


class PostUpdateRequest(BaseModel):
    cong_dong_id: int | None = Field(default=None, gt=0)
    noi_dung: str | None = None
    danh_muc: str | None = Field(default=None, max_length=30)
    tep_dinh_kem: str | None = Field(default=None, max_length=500)


class CommentCreateRequest(BaseModel):
    noi_dung: str = Field(..., min_length=1, max_length=2000)


class FriendRequestCreate(BaseModel):
    ma_nguoi_nhan: int = Field(..., gt=0)


class FriendRespondRequest(BaseModel):
    chap_nhan: bool | None = None
    trang_thai: str | None = Field(default=None, max_length=20)


@router.get("/status")
def module_status():
    return {
        "ok": True,
        **model.get_module_health(),
        "endpoints": [
            "GET /api/m03/posts",
            "POST /api/m03/posts",
            "GET /api/m03/posts/{id}",
            "PUT /api/m03/posts/{id}",
            "DELETE /api/m03/posts/{id}",
            "GET /api/m03/posts/{id}/comments",
            "POST /api/m03/posts/{id}/comments",
            "DELETE /api/m03/posts/{postId}/comments/{commentId}",
            "POST /api/m03/posts/{id}/like",
            "GET /api/m03/friends/search",
            "GET /api/m03/friends",
            "POST /api/m03/friends/request",
            "PUT /api/m03/friends/{id}/respond",
            "DELETE /api/m03/friends/{id}",
        ],
    }


@router.get("/posts")
def list_posts(
    current_user: CurrentUser,
    cong_dong_id: int | None = Query(default=None),
    danh_muc: str | None = Query(default=None),
    search: str = Query(default=""),
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    data = service.list_posts(
        viewer_id=current_user["user_id"],
        cong_dong_id=cong_dong_id,
        danh_muc=danh_muc,
        search=search,
        limit=limit,
        offset=offset,
    )
    return {"ok": True, **data}


@router.get("/posts/{post_id}")
def get_post_detail(post_id: int, current_user: CurrentUser):
    data = service.get_post_detail(post_id=post_id, viewer_id=current_user["user_id"])
    return {"ok": True, **data}


@router.post("/posts", status_code=201)
def create_post(payload: PostCreateRequest, current_user: CurrentUser):
    return service.create_post(
        user_id=current_user["user_id"],
        cong_dong_id=payload.cong_dong_id,
        noi_dung=payload.noi_dung,
        danh_muc=payload.danh_muc,
        tep_dinh_kem=payload.tep_dinh_kem,
    )


@router.put("/posts/{post_id}")
def update_post(post_id: int, payload: PostUpdateRequest, current_user: CurrentUser):
    return service.update_post(
        post_id=post_id,
        user_id=current_user["user_id"],
        noi_dung=payload.noi_dung,
        danh_muc=payload.danh_muc,
        cong_dong_id=payload.cong_dong_id,
        tep_dinh_kem=payload.tep_dinh_kem,
        tep_dinh_kem_provided="tep_dinh_kem" in payload.model_fields_set,
    )


@router.delete("/posts/{post_id}")
def delete_post(post_id: int, current_user: CurrentUser):
    return service.delete_post(post_id=post_id, user_id=current_user["user_id"])


@router.get("/posts/{post_id}/comments")
def list_post_comments(post_id: int, current_user: CurrentUser):
    data = service.list_post_comments(post_id=post_id, viewer_id=current_user["user_id"])
    return {"ok": True, **data}


@router.post("/posts/{post_id}/comments", status_code=201)
def add_comment(post_id: int, payload: CommentCreateRequest, current_user: CurrentUser):
    return service.add_comment(
        post_id=post_id,
        user_id=current_user["user_id"],
        actor_name=current_user.get("full_name") or current_user.get("email") or "Sinh viên",
        noi_dung=payload.noi_dung,
    )


@router.delete("/posts/{post_id}/comments/{comment_id}")
def delete_comment(post_id: int, comment_id: int, current_user: CurrentUser):
    return service.delete_comment(
        post_id=post_id,
        comment_id=comment_id,
        user_id=current_user["user_id"],
    )


@router.post("/posts/{post_id}/like")
def toggle_like(post_id: int, current_user: CurrentUser):
    return service.toggle_like(
        post_id=post_id,
        user_id=current_user["user_id"],
        actor_name=current_user.get("full_name") or current_user.get("email") or "Sinh viên",
    )


@router.get("/friends/search")
def search_students(
    current_user: CurrentUser,
    q: str = Query(default=""),
    lop_id: int | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=100),
):
    data = service.search_students(
        viewer_id=current_user["user_id"],
        query=q,
        lop_id=lop_id,
        limit=limit,
    )
    return {"ok": True, **data}


@router.get("/friends")
def list_friends(current_user: CurrentUser):
    data = service.list_friends_and_requests(user_id=current_user["user_id"])
    return {"ok": True, **data}


@router.post("/friends/request", status_code=201)
def send_friend_request(payload: FriendRequestCreate, current_user: CurrentUser):
    return service.send_friend_request(
        sender_id=current_user["user_id"],
        sender_name=current_user.get("full_name") or current_user.get("email") or "Sinh viên",
        target_id=payload.ma_nguoi_nhan,
    )


@router.put("/friends/{friendship_id}/respond")
def respond_friend_request(
    friendship_id: int,
    payload: FriendRespondRequest,
    current_user: CurrentUser,
):
    accepted = payload.chap_nhan
    if accepted is None and payload.trang_thai is not None:
        if payload.trang_thai == "BanBe":
            accepted = True
        elif payload.trang_thai == "TuChoi":
            accepted = False
        else:
            raise HTTPException(status_code=400, detail="trang_thai phải là 'BanBe' hoặc 'TuChoi'.")
    if accepted is None:
        raise HTTPException(status_code=400, detail="Cần truyền 'chap_nhan' hoặc 'trang_thai'.")

    return service.respond_friend_request(
        friendship_id=friendship_id,
        user_id=current_user["user_id"],
        responder_name=current_user.get("full_name") or current_user.get("email") or "Sinh viên",
        chap_nhan=accepted,
    )


@router.delete("/friends/{friendship_id}")
def delete_friendship(friendship_id: int, current_user: CurrentUser):
    return service.remove_friendship(friendship_id=friendship_id, user_id=current_user["user_id"])
