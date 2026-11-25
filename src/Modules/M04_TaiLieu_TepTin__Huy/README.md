# M4 — Tài liệu Học tập & Truyền tệp

- **Thành viên sở hữu (End-to-End):** Huy (Full-stack Module)
- **Thư mục MVC:** `src/Modules/M04_TaiLieu_TepTin__Huy`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `MonHoc`, `TaiLieu`, `DanhGiaTaiLieu`
- **Endpoints / WebSocket dự kiến:**
  - `GET /api/m04/subjects`
  - `POST /api/m04/documents/upload`
  - `GET /api/m04/documents/search`
  - `GET /api/m04/documents/{id}/download`
  - `POST /api/m04/documents/{id}/rate`

## Phạm vi chức năng
Danh mục MonHoc; Tải lên tài liệu (<20MB PDF/DOCX/ảnh) lưu thông tin thẳng vào bảng TaiLieu; Tải tệp về máy và cộng SoLuotTai; Tìm kiếm theo môn & Chấm điểm 1–5★ (DanhGiaTaiLieu).

## Quy trình 4 Bước hoàn thành
- **B1 (Model 3 bảng Tài liệu):** Tạo Model cho MonHoc, TaiLieu (lưu kèm TenTep, DuongDanTep, SoLuotTai) và DanhGiaTaiLieu (1–5★).
- **B2 (Controller Upload/Download):** Viết API nhận file multipart (<20MB), tải về FileResponse cộng SoLuotTai và tính lại DiemDanhGiaTB.
- **B3 (Tkinter Desktop View):** Dựng màn hình tìm tài liệu theo môn, filedialog chọn file + thanh tiến trình và chấm 1–5 sao.
- **B4 (Demo & KPI):** Test từ chối tệp vượt quá 20MB/sai loại, tải lên PDF thành công, tải về máy & chấm 5★.

**KPI:** Truyền nhận tệp nguyên vẹn, kiểm tra định dạng/dung lượng an toàn, cập nhật điểm TB chuẩn xác.
