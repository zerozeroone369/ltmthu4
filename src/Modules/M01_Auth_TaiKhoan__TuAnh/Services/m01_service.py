"""Business logic cho M1: Auth, JWT, Hồ sơ, Riêng tư & OTP Quên mật khẩu (Nguyễn Ngô Tú Anh)."""
from __future__ import annotations

import json
import os
import re
import secrets
import smtplib
from datetime import UTC, datetime
from email.message import EmailMessage

from fastapi import HTTPException
from passlib.context import CryptContext

from src.Shared.middlewares.auth_middleware import create_access_token, revoke_token

from ..Models import m01_model as model

_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PRIVACY_ALLOWED_VALUES = {"CongDong", "BanBe", "ChiMinhToi"}
_PRIVACY_ALLOWED_KEYS = {"hienSdt", "hienEmail", "hienBaiViet"}
_DEFAULT_PRIVACY = {"hienSdt": "BanBe", "hienEmail": "CongDong", "hienBaiViet": "CongDong"}


def normalize_email(email: str) -> str:
    cleaned = email.strip().lower()
    if not _EMAIL_RE.match(cleaned) or len(cleaned) > 254:
        raise HTTPException(status_code=400, detail="Địa chỉ email không hợp lệ.")
    return cleaned


def validate_password_policy(password: str) -> str:
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 6 ký tự.")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Mật khẩu không được vượt quá 72 byte.")
    return password


def hash_password(plain_password: str) -> str:
    validate_password_policy(plain_password)
    return _PWD_CONTEXT.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    if not plain_password or not password_hash:
        return False
    try:
        return _PWD_CONTEXT.verify(plain_password, password_hash)
    except (ValueError, TypeError):
        return False


def parse_privacy_settings(raw_value: str | dict | None) -> dict:
    parsed = dict(_DEFAULT_PRIVACY)
    if isinstance(raw_value, dict):
        parsed.update({k: v for k, v in raw_value.items() if k in _PRIVACY_ALLOWED_KEYS})
        return parsed
    if isinstance(raw_value, str) and raw_value.strip():
        try:
            data = json.loads(raw_value)
            if isinstance(data, dict):
                parsed.update({k: v for k, v in data.items() if k in _PRIVACY_ALLOWED_KEYS})
        except json.JSONDecodeError:
            pass
    return parsed


def sanitize_user(row: dict, community_chain: list[dict] | None = None) -> dict:
    """Strip sensitive fields (MatKhauHash, MaOTP, HanOTP) before returning user JSON."""
    clean = {
        k: v
        for k, v in row.items()
        if k not in {"MatKhauHash", "MaOTP", "HanOTP"}
    }
    clean["CaiDatRiengTu"] = parse_privacy_settings(row.get("CaiDatRiengTu"))
    if community_chain is not None:
        clean["community_chain"] = community_chain
    return clean


def _load_chain_for_user(row: dict) -> list[dict]:
    lop_id = row.get("MaLop")
    if not lop_id:
        return []
    return model.get_community_chain(int(lop_id))


def list_community_children(parent_id: int | None = None) -> list[dict]:
    return model.get_community_children(parent_id)


def fetch_community_chain(lop_id: int) -> list[dict]:
    chain = model.get_community_chain(lop_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị cộng đồng.")
    return chain


def register_student(
    *,
    email: str,
    password: str,
    ho_ten: str,
    ma_lop: int | None = None,
    ma_sinh_vien: str | None = None,
    so_dien_thoai: str | None = None,
    gioi_thieu: str | None = None,
) -> dict:
    norm_email = normalize_email(email)
    full_name = ho_ten.strip()
    if not full_name:
        raise HTTPException(status_code=400, detail="Họ tên không được để trống.")

    if ma_lop is not None:
        lop = model.get_active_class_by_id(ma_lop)
        if not lop:
            raise HTTPException(status_code=400, detail="Lớp sinh hoạt không hợp lệ hoặc không còn hoạt động.")

    mssv = ma_sinh_vien.strip() if ma_sinh_vien and ma_sinh_vien.strip() else None
    phone = so_dien_thoai.strip() if so_dien_thoai and so_dien_thoai.strip() else None
    bio = gioi_thieu.strip() if gioi_thieu and gioi_thieu.strip() else None
    pw_hash = hash_password(password)

    try:
        # Always enforce SinhVien role on self-registration regardless of client payload.
        created = model.create_user(
            {
                "MaLop": ma_lop,
                "VaiTro": "SinhVien",
                "MaSinhVien": mssv,
                "Email": norm_email,
                "MatKhauHash": pw_hash,
                "HoTen": full_name,
                "SoDienThoai": phone,
                "GioiThieu": bio,
            }
        )
    except ValueError as exc:
        code = str(exc)
        if code == "DUPLICATE_MSSV":
            raise HTTPException(status_code=409, detail="Mã sinh viên đã được đăng ký.") from exc
        raise HTTPException(status_code=409, detail="Email đã tồn tại trong hệ thống.") from exc

    token, expires_in = create_access_token(
        created["MaNguoiDung"], created["Email"], created["VaiTro"]
    )
    chain = _load_chain_for_user(created)
    return {
        "ok": True,
        "message": "Đăng ký tài khoản thành công.",
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": sanitize_user(created, chain),
    }


def login_user(*, email: str, password: str) -> dict:
    norm_email = normalize_email(email)
    user = model.get_user_by_email(norm_email)
    if not user or not verify_password(password, user.get("MatKhauHash", "")):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")

    if user.get("TrangThai") != "HoatDong":
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa hoặc ngừng hoạt động.")

    token, expires_in = create_access_token(
        user["MaNguoiDung"], user["Email"], user["VaiTro"]
    )
    chain = _load_chain_for_user(user)
    return {
        "ok": True,
        "message": "Đăng nhập thành công.",
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": sanitize_user(user, chain),
    }


def logout_user(token_payload: dict) -> dict:
    revoke_token(token_payload)
    return {"ok": True, "message": "Đăng xuất thành công."}


def get_my_profile(user_id: int) -> dict:
    user = model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    chain = _load_chain_for_user(user)
    return {"ok": True, "user": sanitize_user(user, chain)}


def change_password(*, user_id: int, old_password: str, new_password: str) -> dict:
    user = model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    if not verify_password(old_password, user.get("MatKhauHash", "")):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")
    if old_password == new_password:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải khác mật khẩu hiện tại.")

    new_hash = hash_password(new_password)
    model.update_password_hash(user_id, new_hash)
    return {"ok": True, "message": "Đổi mật khẩu thành công."}


def _try_send_otp_email(to_email: str, full_name: str, otp_code: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    if not smtp_host:
        return False
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASSWORD", "").strip()
    sender = os.getenv("SMTP_FROM", smtp_user or "no-reply@mxh-sinhvien.local")

    msg = EmailMessage()
    msg["Subject"] = "Mã xác thực OTP đặt lại mật khẩu — MXH Sinh Viên"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        f"Xin chào {full_name},\n\n"
        f"Mã OTP đặt lại mật khẩu của bạn là: {otp_code}\n"
        "Mã có hiệu lực trong 10 phút. Vui lòng không chia sẻ mã này cho người khác.\n"
    )
    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
        server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    return True


def request_forgot_otp(*, email: str) -> dict:
    norm_email = normalize_email(email)
    user = model.get_user_by_email(norm_email)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản với email này.")
    if user.get("TrangThai") != "HoatDong":
        raise HTTPException(status_code=403, detail="Tài khoản đang bị khóa, không thể đặt lại mật khẩu.")

    otp_code = f"{secrets.randbelow(1_000_000):06d}"
    model.save_otp(user["MaNguoiDung"], otp_code, expires_minutes=10)

    sent_via_email = False
    try:
        sent_via_email = _try_send_otp_email(norm_email, user["HoTen"], otp_code)
    except (smtplib.SMTPException, OSError):
        sent_via_email = False

    resp: dict = {
        "ok": True,
        "expires_in_minutes": 10,
        "sent_via_email": sent_via_email,
        "message": (
            "Mã OTP 6 số đã được gửi tới email của bạn."
            if sent_via_email
            else "Đã tạo mã OTP 6 số (chế độ demo không cấu hình SMTP)."
        ),
    }
    if not sent_via_email:
        resp["demo_otp"] = otp_code
    return resp


def reset_password_with_otp(*, email: str, otp: str, new_password: str) -> dict:
    norm_email = normalize_email(email)
    user = model.get_user_by_email(norm_email)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản với email này.")
    if user.get("TrangThai") != "HoatDong":
        raise HTTPException(status_code=403, detail="Tài khoản đang bị khóa.")

    stored_otp = (user.get("MaOTP") or "").strip()
    expires_at = user.get("HanOTP")
    provided_otp = otp.strip()

    if not stored_otp or not expires_at:
        raise HTTPException(status_code=400, detail="Chưa có yêu cầu mã OTP hoặc mã đã được sử dụng.")

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if datetime.now(UTC) > expires_at:
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn, vui lòng yêu cầu mã mới.")

    if not secrets.compare_digest(stored_otp, provided_otp):
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác.")

    new_hash = hash_password(new_password)
    model.reset_password_with_otp(user["MaNguoiDung"], new_hash)
    return {"ok": True, "message": "Đặt lại mật khẩu thành công. Bạn có thể đăng nhập bằng mật khẩu mới."}


def update_profile_and_privacy(
    *,
    user_id: int,
    ho_ten: str | None = None,
    so_dien_thoai: str | None = None,
    anh_dai_dien: str | None = None,
    gioi_thieu: str | None = None,
    ma_sinh_vien: str | None = None,
    ma_lop: int | None = None,
    cai_dat_rieng_tu: dict | None = None,
) -> dict:
    existing = model.get_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    updates: dict[str, object] = {}
    if ho_ten is not None:
        cleaned_name = ho_ten.strip()
        if not cleaned_name:
            raise HTTPException(status_code=400, detail="Họ tên không được để trống.")
        updates["HoTen"] = cleaned_name

    if so_dien_thoai is not None:
        updates["SoDienThoai"] = so_dien_thoai.strip() or None
    if anh_dai_dien is not None:
        updates["AnhDaiDien"] = anh_dai_dien.strip() or None
    if gioi_thieu is not None:
        updates["GioiThieu"] = gioi_thieu.strip() or None
    if ma_sinh_vien is not None:
        updates["MaSinhVien"] = ma_sinh_vien.strip() or None

    if ma_lop is not None:
        lop = model.get_active_class_by_id(ma_lop)
        if not lop:
            raise HTTPException(status_code=400, detail="Lớp sinh hoạt mới không hợp lệ hoặc không còn hoạt động.")
        updates["MaLop"] = ma_lop

    if cai_dat_rieng_tu is not None:
        merged_privacy = parse_privacy_settings(existing.get("CaiDatRiengTu"))
        for key, val in cai_dat_rieng_tu.items():
            if key not in _PRIVACY_ALLOWED_KEYS:
                raise HTTPException(status_code=400, detail=f"Tùy chọn riêng tư không hợp lệ: {key}")
            if val not in _PRIVACY_ALLOWED_VALUES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Giá trị quyền riêng tư '{val}' phải thuộc {sorted(_PRIVACY_ALLOWED_VALUES)}.",
                )
            merged_privacy[key] = val
        updates["CaiDatRiengTu"] = json.dumps(merged_privacy, ensure_ascii=False)

    try:
        updated = model.update_user_profile(user_id, updates)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail="Mã sinh viên đã thuộc về tài khoản khác.") from exc

    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    chain = _load_chain_for_user(updated)
    return {
        "ok": True,
        "message": "Cập nhật hồ sơ thành công.",
        "user": sanitize_user(updated, chain),
    }
