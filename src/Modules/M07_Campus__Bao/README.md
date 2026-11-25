# M7 — Campus (Tin tức, Học bổng, Sự kiện)

- **Thành viên sở hữu (End-to-End):** Bảo (Full-stack Module)
- **Thư mục MVC:** `src/Modules/M07_Campus__Bao`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `TinTruong`
- **Endpoints / WebSocket dự kiến:**
  - `GET /api/m07/campus`
  - `POST /api/m07/admin/campus`
  - `PUT /api/m07/admin/campus/{id}`
  - `DELETE /api/m07/admin/campus/{id}`

## Phạm vi chức năng
Sinh viên xem & lọc tin nhà trường (SuKien, HocBong, ThucTap, CLB, ThongBao) theo CongDong; Admin đăng mới, chỉnh sửa, ẩn/xóa tin Campus và phát thông báo tới sinh viên.

## Quy trình 4 Bước hoàn thành
- **B1 (Model TinTruong):** Viết Model truy vấn TinTruong (lọc TrangThai = 'CongBo', phân trang LIMIT/OFFSET).
- **B2 (Controller & Phân quyền):** Viết API cho sinh viên lọc tin và API cho Admin đăng/sửa/ẩn tin kèm đẩy thông báo M09.
- **B3 (Tkinter Desktop View):** Dựng tab Campus cho Sinh viên và Frame đăng tin gắn vào màn hình Admin M10.
- **B4 (Demo & KPI):** Test Admin đăng tin Sự kiện/Học bổng mới → Sinh viên mở tab Campus thấy ngay lập tức.

**KPI:** Tin mới hiển thị đúng chuyên mục và phạm vi Trường/Khoa, chỉ Admin được quyền đăng/sửa.
