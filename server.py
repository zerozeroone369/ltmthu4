"""
Máy chủ Python Server – Client (FastAPI + WebSocket + PostgreSQL) deploy lên Render.
Cung cấp:
  - /ws           : Kênh WebSocket hai chiều cho App Desktop Tkinter
  - /api/m01..m10 : Các Controller theo 10 Module MVC
  - /health       : Kiểm tra kết nối PostgreSQL 18 bảng & trạng thái Server cho Render
  - /             : Trang Giám sát trạng thái Server (dành cho giảng viên kiểm tra link Cloud)
  - /docs         : Tài liệu API Swagger của FastAPI
"""
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.Shared.config.db import check_db_health
from src.Shared.middlewares.realtime_helper import manager

from src.Modules.M01_Auth_TaiKhoan__TuAnh.Controllers.m01_controller import router as m01_router
from src.Modules.M02_CongDong_5Cap__Duy.Controllers.m02_controller import router as m02_router
from src.Modules.M03_BaiViet_KetBan__Duy.Controllers.m03_controller import router as m03_router
from src.Modules.M04_TaiLieu_TepTin__Huy.Controllers.m04_controller import router as m04_router
from src.Modules.M05_HoiDap_QA__Huy.Controllers.m05_controller import router as m05_router
from src.Modules.M06_NhomHoc__Bao.Controllers.m06_controller import router as m06_router
from src.Modules.M07_Campus__Bao.Controllers.m07_controller import router as m07_router
from src.Modules.M08_BangTin_RiengTu__Thai.Controllers.m08_controller import router as m08_router
from src.Modules.M09_Chat_ThongBao_Realtime__Thai.Controllers.m09_controller import router as m09_router
from src.Modules.M10_QuanTri_KiemDuyet__TuAnh.Controllers.m10_controller import router as m10_router

load_dotenv()

app = FastAPI(
    title="MXH Sinh Viên — Server Python (Lập trình mạng Server–Client)",
    version="1.0.0",
)

for r in (
    m01_router, m02_router, m03_router, m04_router, m05_router,
    m06_router, m07_router, m08_router, m09_router, m10_router,
):
    app.include_router(r)

MODULES_SUMMARY = [{"id": "M1", "code": "m01", "name": "Tài khoản, Hồ sơ & Quên mật khẩu (OTP)", "owner": "Nguyễn Ngô Tú Anh", "tables": ["NguoiDung"]}, {"id": "M2", "code": "m02", "name": "Cây Cộng đồng 5 Cấp (Trường → Lớp)", "owner": "Duy", "tables": ["CongDong"]}, {"id": "M3", "code": "m03", "name": "Bài viết, Tương tác & Kết bạn", "owner": "Duy", "tables": ["BaiViet", "BinhLuan", "TuongTac", "KetBan"]}, {"id": "M4", "code": "m04", "name": "Tài liệu Học tập & Truyền tệp", "owner": "Huy", "tables": ["MonHoc", "TaiLieu", "DanhGiaTaiLieu"]}, {"id": "M5", "code": "m05", "name": "Hỏi đáp Học thuật (Q&A & Upvote)", "owner": "Huy", "tables": ["CauHoi", "CauTraLoi", "BinhChonCauTraLoi"]}, {"id": "M6", "code": "m06", "name": "Nhóm học Tập (Study Groups)", "owner": "Bảo", "tables": ["NhomHoc", "ThanhVienNhom"]}, {"id": "M7", "code": "m07", "name": "Campus (Tin tức, Học bổng, Sự kiện)", "owner": "Bảo", "tables": ["TinTruong"]}, {"id": "M8", "code": "m08", "name": "Khung Tkinter Chung, Bảng tin & Riêng tư", "owner": "Thái", "tables": ["NguoiDung", "KetBan"]}, {"id": "M9", "code": "m09", "name": "Nhắn tin Realtime & Thông báo", "owner": "Thái", "tables": ["TinNhan", "ThongBao"]}, {"id": "M10", "code": "m10", "name": "Quản trị Hệ thống & Kiểm duyệt (Admin)", "owner": "Nguyễn Ngô Tú Anh", "tables": ["BaoCaoViPham", "NguoiDung"]}]


@app.get("/health")
def health_check():
    db_info = check_db_health()
    return {
        "status": "ok",
        "language": "Python 3 (FastAPI + WebSocket Server / Tkinter Desktop Client)",
        "database": "PostgreSQL 18 core tables",
        "cloud": "Render",
        "online_clients": len(manager.active_clients),
        "db_status": db_info,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = "guest"):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"event": "ack", "received": data})
    except WebSocketDisconnect:
        manager.disconnect(user_id)


@app.get("/", response_class=HTMLResponse)
def server_status_dashboard():
    db_info = check_db_health()
    db_badge = (
        f"PostgreSQL: Đã kết nối ({db_info['tables']} bảng)"
        if db_info.get("connected")
        else f"PostgreSQL: {db_info.get('detail')}"
    )
    badge_bg = "#dcfce7" if db_info.get("connected") else "#fef3c7"
    badge_fg = "#15803d" if db_info.get("connected") else "#92400e"

    cards_html = "".join(
        f"""
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
          <div style="font-size:12px;font-weight:700;color:#2563eb;">{m["id"]} · {m["owner"]}</div>
          <div style="font-size:15px;font-weight:700;margin:4px 0;">{m["name"]}</div>
          <div style="font-size:12px;color:#475569;margin-bottom:8px;">Bảng SQL: {", ".join(m["tables"])}</div>
          <a href="/api/{m['code']}/status" style="font-size:12px;color:#1d4ed8;text-decoration:none;font-weight:600;">/api/{m["code"]}/status →</a>
        </div>"""
        for m in MODULES_SUMMARY
    )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"><title>Server Monitor — MXH Sinh Viên (Python + Render)</title></head>
<body style="font-family:system-ui,sans-serif;background:#f1f5f9;color:#0f172a;margin:0;padding:28px;">
  <div style="max-width:1080px;margin:auto;">
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
      <div>
        <h1 style="margin:0;font-size:20px;">Server Giám Sát — Mạng Xã Hội Sinh Viên (Python Server–Client)</h1>
        <p style="margin:4px 0 0;color:#475569;font-size:13px;">Ngôn ngữ: <b>Python 3 (FastAPI + WebSocket / Tkinter Client)</b> • CSDL: <b>PostgreSQL (18 bảng)</b> • Cloud: <b>Render</b></p>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
        <span style="padding:6px 10px;border-radius:999px;font-size:12px;font-weight:700;background:{badge_bg};color:{badge_fg};">{db_badge}</span>
        <span style="padding:6px 10px;border-radius:999px;font-size:12px;font-weight:700;background:#eff6ff;color:#1d4ed8;">WebSocket Online: {len(manager.active_clients)} Client</span>
        <a href="/health" style="padding:7px 12px;background:#2563eb;color:#fff;text-decoration:none;border-radius:8px;font-size:12.5px;font-weight:600;">Health JSON (/health)</a>
        <a href="/docs" style="padding:7px 12px;background:#fff;border:1px solid #cbd5e1;color:#0f172a;text-decoration:none;border-radius:8px;font-size:12.5px;font-weight:600;">API Docs (/docs)</a>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;">{cards_html}</div>
  </div>
</body>
</html>"""
