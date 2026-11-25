# M8 — Khung Tkinter Chung, Bảng tin & Riêng tư

- **Thành viên sở hữu (End-to-End):** Thái (UI Lead)
- **Thư mục MVC:** `src/Modules/M08_BangTin_RiengTu__Thai`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `NguoiDung`, `KetBan`
- **Endpoints / WebSocket dự kiến:**
  - `GET /api/m08/feed`
  - `PUT /api/m08/privacy`
  - `POST /api/m08/block/{targetId}`
  - `DELETE /api/m08/block/{targetId}`

## Phạm vi chức năng
Dựng khung cửa sổ Tkinter chính (Sidebar, Header, chuyển đổi 10 Module trong client_app.py) cho cả nhóm; Bảng tin thông minh lọc theo 5 cấp cộng đồng & 4 chủ đề; Quyền riêng tư (CaiDatRiengTu trong NguoiDung) & Chặn người dùng (KetBan DaChan).

## Quy trình 4 Bước hoàn thành
- **B1 (Model Feed & Riêng tư):** Viết truy vấn hợp nhất Bảng tin từ BaiViet/TaiLieu/CauHoi/TinTruong và đọc/lưu CaiDatRiengTu, trạng thái DaChan.
- **B2 (Controller & Lọc quyền):** Viết Controller GET /api/m08/feed ưu tiên nội dung từ Lớp → Trường, đồng thời ẩn bài của người đang bị chặn.
- **B3 (Tkinter Layout & Views):** Dựng khung client_app.py để các thành viên nhúng View vào, cùng màn hình Bảng tin & Cài đặt riêng tư.
- **B4 (Demo & KPI):** Test ẩn SĐT/Email và chặn 1 tài khoản → người bị chặn không thấy thông tin riêng tư và không nhắn tin được.

**KPI:** Khung App Desktop thống nhất cho 5 thành viên, Bảng tin tải nhanh và tôn trọng đúng quyền riêng tư.
