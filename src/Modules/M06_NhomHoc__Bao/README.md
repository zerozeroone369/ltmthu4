# M6 — Nhóm học Tập (Study Groups)

- **Thành viên sở hữu (End-to-End):** Bảo (Full-stack Module)
- **Thư mục MVC:** `src/Modules/M06_NhomHoc__Bao`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `NhomHoc`, `ThanhVienNhom`
- **Endpoints / WebSocket dự kiến:**
  - `POST /api/m06/groups`
  - `GET /api/m06/groups/search`
  - `POST /api/m06/groups/{id}/join`
  - `PUT /api/m06/groups/{id}/requests/{uid}`
  - `PUT /api/m06/groups/{id}/capacity`
  - `POST /api/m06/groups/{id}/transfer-leave`

## Phạm vi chức năng
Sinh viên tạo nhóm học (thành Trưởng nhóm); Tìm & Gửi đơn xin gia nhập (lưu ngay vào ThanhVienNhom trạng thái 'ChoDuyet'); Trưởng nhóm duyệt/từ chối theo sĩ số tối đa; Đổi sức chứa & Bàn giao trưởng nhóm khi rời.

## Quy trình 4 Bước hoàn thành
- **B1 (Model 2 bảng Nhóm):** Tạo Model cho NhomHoc và ThanhVienNhom (dùng TrangThai ChoDuyet/DaThamGia/TuChoi thay vì tách nhiều bảng).
- **B2 (Controller & Sĩ số):** Viết API tạo nhóm, gửi đơn, duyệt đơn (kiểm tra SoThanhVienHienTai < SoThanhVienToiDa) và chuyển trưởng nhóm.
- **B3 (Tkinter Desktop View):** Dựng danh sách nhóm học, khung duyệt đơn của Trưởng nhóm & hộp chọn người kế nhiệm khi rời nhóm.
- **B4 (Demo & KPI):** Test xin vào nhóm → Trưởng nhóm duyệt sát sĩ số → Trưởng nhóm chuyển quyền rồi rời nhóm.

**KPI:** Không bao giờ vượt sĩ số tối đa hay để nhóm vô chủ khi Trưởng nhóm rời đi.
