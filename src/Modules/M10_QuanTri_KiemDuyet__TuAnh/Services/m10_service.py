"""Business logic cho M10: Quản trị Hệ thống & Kiểm duyệt Vi phạm (Nguyễn Ngô Tú Anh)."""
from __future__ import annotations

import asyncio

from fastapi import HTTPException

from src.Shared.middlewares.realtime_helper import manager

from ..Models import m10_model as model

_VALID_USER_STATUSES = {"HoatDong", "BiKhoa"}
_VALID_ROLES = {"SinhVien", "QuanTriVien"}
_VALID_DECISIONS = {"BacBo", "AnNoiDung", "XoaMem", "KhoaTaiKhoan"}


def _push_realtime_best_effort(notifications: list[dict]) -> None:
    """Dispatch WebSocket notifications when running inside an active asyncio event loop."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    for item in notifications:
        loop.create_task(
            manager.send_notification(
                str(item["MaNguoiNhan"]),
                "notification",
                {
                    "type": item["LoaiThongBao"],
                    "content": item["NoiDung"],
                    "link": item.get("LienKet"),
                },
            )
        )


def list_admin_users(
    *,
    search: str = "",
    vai_tro: str | None = None,
    trang_thai: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    if vai_tro and vai_tro not in _VALID_ROLES:
        raise HTTPException(status_code=400, detail="Vai trò lọc không hợp lệ.")
    if trang_thai and trang_thai not in _VALID_USER_STATUSES:
        raise HTTPException(status_code=400, detail="Trạng thái lọc không hợp lệ.")

    data = model.list_users(
        search=search,
        vai_tro=vai_tro,
        trang_thai=trang_thai,
        limit=limit,
        offset=offset,
    )
    return {"ok": True, **data}


def set_user_lock_status(*, admin_id: int, target_user_id: int, trang_thai: str) -> dict:
    if trang_thai not in _VALID_USER_STATUSES:
        raise HTTPException(status_code=400, detail="Trạng thái tài khoản phải là 'HoatDong' hoặc 'BiKhoa'.")

    target = model.get_user_by_id(target_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    if (
        trang_thai == "BiKhoa"
        and target["VaiTro"] == "QuanTriVien"
        and target["TrangThai"] == "HoatDong"
        and model.count_active_admins() <= 1
    ):
        if target_user_id == admin_id:
            raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản Quản trị viên đang đăng nhập.")
        raise HTTPException(
            status_code=400,
            detail="Không thể khóa Quản trị viên cuối cùng đang hoạt động trong hệ thống.",
        )
    if trang_thai == "BiKhoa" and target_user_id == admin_id:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản Quản trị viên đang đăng nhập.")

    updated = model.update_user_lock_status(target_user_id, trang_thai)
    action_label = "khóa" if trang_thai == "BiKhoa" else "mở khóa"
    return {
        "ok": True,
        "message": f"Đã {action_label} tài khoản {updated['HoTen']}.",
        "user": updated,
    }


def change_user_role(*, admin_id: int, target_user_id: int, vai_tro: str) -> dict:
    if vai_tro not in _VALID_ROLES:
        raise HTTPException(status_code=400, detail="Vai trò phải là 'SinhVien' hoặc 'QuanTriVien'.")

    target = model.get_user_by_id(target_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    if (
        target["VaiTro"] == "QuanTriVien"
        and vai_tro == "SinhVien"
        and target["TrangThai"] == "HoatDong"
        and model.count_active_admins() <= 1
    ):
        raise HTTPException(
            status_code=400,
            detail="Không thể thu hồi quyền của Quản trị viên cuối cùng đang hoạt động.",
        )

    updated = model.update_user_role(target_user_id, vai_tro)
    return {
        "ok": True,
        "message": f"Đã cập nhật vai trò của {updated['HoTen']} thành {vai_tro}.",
        "user": updated,
    }


def submit_report(
    *,
    reporter_id: int,
    loai_noi_dung: str,
    id_noi_dung: int,
    ly_do: str,
    chi_tiet: str | None = None,
) -> dict:
    if loai_noi_dung not in model.CONTENT_TARGETS:
        raise HTTPException(
            status_code=400,
            detail=f"Loại nội dung phải thuộc {sorted(model.CONTENT_TARGETS)}.",
        )
    reason = ly_do.strip()
    if not reason:
        raise HTTPException(status_code=400, detail="Vui lòng nhập lý do báo cáo.")

    target = model.get_content_target(loai_noi_dung, id_noi_dung)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy nội dung hoặc tài khoản cần báo cáo.")

    detail_text = chi_tiet.strip() if chi_tiet and chi_tiet.strip() else None
    report = model.create_report(reporter_id, loai_noi_dung, id_noi_dung, reason, detail_text)
    return {
        "ok": True,
        "message": "Đã gửi báo cáo vi phạm lên Quản trị viên.",
        "report": report,
    }


def list_admin_reports(
    *,
    trang_thai: str | None = None,
    loai_noi_dung: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    if trang_thai and trang_thai not in {"ChoDuyet", "DaXuLy", "TuChoi"}:
        raise HTTPException(status_code=400, detail="Trạng thái báo cáo không hợp lệ.")
    if loai_noi_dung and loai_noi_dung not in model.CONTENT_TARGETS:
        raise HTTPException(status_code=400, detail="Loại nội dung lọc không hợp lệ.")

    data = model.list_reports(
        trang_thai=trang_thai,
        loai_noi_dung=loai_noi_dung,
        limit=limit,
        offset=offset,
    )
    return {"ok": True, **data}


def moderate_report(
    *,
    admin_id: int,
    report_id: int,
    quyet_dinh: str,
    ghi_chu_xu_ly: str | None = None,
) -> dict:
    if quyet_dinh not in _VALID_DECISIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Quyết định xử lý phải thuộc {sorted(_VALID_DECISIONS)}.",
        )

    report = model.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn báo cáo vi phạm.")
    if report["TrangThai"] != "ChoDuyet":
        raise HTTPException(status_code=409, detail="Đơn báo cáo này đã được xử lý trước đó.")

    loai = report["LoaiNoiDung"]
    target_id = int(report["IdNoiDung"])
    target = model.get_content_target(loai, target_id)
    meta = model.CONTENT_TARGETS.get(loai) or {}

    note = ghi_chu_xu_ly.strip() if ghi_chu_xu_ly and ghi_chu_xu_ly.strip() else None
    report_status = "DaXuLy"
    content_status: str | None = None
    lock_owner_id: int | None = None

    if quyet_dinh == "BacBo":
        report_status = "TuChoi"
    elif quyet_dinh in {"AnNoiDung", "XoaMem"}:
        if loai == "NguoiDung" or not meta.get("status_col"):
            raise HTTPException(
                status_code=400,
                detail=f"Loại '{loai}' không hỗ trợ {quyet_dinh}; vui lòng chọn 'BacBo' hoặc 'KhoaTaiKhoan'.",
            )
        if not target:
            raise HTTPException(status_code=404, detail="Nội dung bị báo cáo không còn tồn tại.")
        content_status = "BiAn" if quyet_dinh == "AnNoiDung" else "DaXoa"
    elif quyet_dinh == "KhoaTaiKhoan":
        if not target or not target.get("owner_id"):
            raise HTTPException(status_code=404, detail="Không xác định được tài khoản liên quan để khóa.")
        owner_id = int(target["owner_id"])
        owner = model.get_user_by_id(owner_id)
        if not owner:
            raise HTTPException(status_code=404, detail="Tài khoản vi phạm không còn tồn tại.")
        if owner_id == admin_id:
            raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản Quản trị viên đang đăng nhập.")
        if (
            owner["VaiTro"] == "QuanTriVien"
            and owner["TrangThai"] == "HoatDong"
            and model.count_active_admins() <= 1
        ):
            raise HTTPException(
                status_code=400,
                detail="Không thể khóa Quản trị viên cuối cùng đang hoạt động trong hệ thống.",
            )
        lock_owner_id = owner_id

    note_suffix = f" Ghi chú: {note}" if note else ""
    notifications: list[dict] = [
        {
            "MaNguoiNhan": int(report["MaNguoiBaoCao"]),
            "MaNguoiThucHien": admin_id,
            "LoaiThongBao": "KiemDuyet",
            "NoiDung": f"Báo cáo #{report_id} ({loai} #{target_id}) đã được xử lý: {quyet_dinh}.{note_suffix}",
            "LienKet": f"/reports/{report_id}",
        }
    ]
    owner_id_val = int(target["owner_id"]) if target and target.get("owner_id") else None
    if quyet_dinh != "BacBo" and owner_id_val and owner_id_val not in {int(report["MaNguoiBaoCao"]), admin_id}:
        notifications.append(
            {
                "MaNguoiNhan": owner_id_val,
                "MaNguoiThucHien": admin_id,
                "LoaiThongBao": "CanhBaoViPham",
                "NoiDung": (
                    f"Nội dung {loai} #{target_id} của bạn đã bị xử lý ({quyet_dinh}) "
                    f"do vi phạm: {report['LyDo']}.{note_suffix}"
                ),
                "LienKet": f"/{loai.lower()}/{target_id}",
            }
        )

    updated_report = model.resolve_report_transaction(
        report_id=report_id,
        admin_id=admin_id,
        quyet_dinh=quyet_dinh,
        ghi_chu_xu_ly=note,
        report_status=report_status,
        content_status=content_status,
        lock_owner_id=lock_owner_id,
        notifications=notifications,
    )
    _push_realtime_best_effort(notifications)
    return {
        "ok": True,
        "message": f"Đã xử lý báo cáo #{report_id} với quyết định '{quyet_dinh}'.",
        "report": updated_report,
    }
