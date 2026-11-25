# M10 — Quản trị Hệ thống & Kiểm duyệt (Admin)

- **Thành viên sở hữu (End-to-End):** Nguyễn Ngô Tú Anh (Leader)
- **Thư mục MVC:** `src/Modules/M10_QuanTri_KiemDuyet__TuAnh`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `BaoCaoViPham`, `NguoiDung`
- **Endpoints / WebSocket dự kiến:**
  - `GET /api/m10/admin/users`
  - `PUT /api/m10/admin/users/{id}/lock`
  - `PUT /api/m10/admin/users/{id}/role`
  - `GET /api/m10/admin/reports`
  - `PUT /api/m10/admin/reports/{id}`

## Phạm vi chức năng
Quản lý danh sách tài khoản (đổi vai trò, khóa/mở khóa chống khóa Admin cuối cùng); Kiểm duyệt đơn BaoCaoViPham (bác bỏ, ẩn, xóa mềm nội dung vi phạm hoặc khóa tài khoản, lưu thẳng kết quả xử lý trên BaoCaoViPham); nhúng View của M02 & M07.

## Quy trình 4 Bước hoàn thành
- **B1 (Model Kiểm duyệt):** Tạo Model Python truy vấn BaoCaoViPham và cập nhật trạng thái/vai trò trên NguoiDung.
- **B2 (Controller Admin):** Viết Controller khóa/đổi vai trò (ngăn khóa Admin cuối) và xử lý báo cáo vi phạm (ẩn/xóa nội dung & gửi thông báo).
- **B3 (Tkinter Admin Dashboard):** Dựng tab Quản lý tài khoản, tab Duyệt báo cáo và ghép View Cây 5 cấp (M02) + Campus (M07) vào chung.
- **B4 (Demo & KPI):** Test báo cáo 1 bài viết → Admin vào duyệt ẩn bài → bài biến mất ngay khỏi Bảng tin sinh viên.

**KPI:** Không khóa nhầm Admin cuối cùng, xử lý báo cáo nhanh gọn và lưu rõ quyết định kiểm duyệt trên BaoCaoViPham.
