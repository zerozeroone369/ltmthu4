# M2 — Cây Cộng đồng 5 Cấp (Trường → Lớp)

- **Thành viên sở hữu (End-to-End):** Duy (Full-stack Module)
- **Thư mục MVC:** `src/Modules/M02_CongDong_5Cap__Duy`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `CongDong`
- **Endpoints / WebSocket dự kiến:**
  - `GET /api/m02/communities/roots`
  - `GET /api/m02/communities/{parentId}/children`
  - `GET /api/m02/communities/chain/{lopId}`
  - `CRUD /api/m02/admin/communities`

## Phạm vi chức năng
Quản lý trọn vẹn 5 cấp (Truong → Khoa → Nganh → KhoaHoc → Lop) trên 1 bảng CongDong tự tham chiếu MaCongDongCha; cấp API lọc nối tiếp cho màn Đăng ký & Hồ sơ; trang Admin sửa/ngừng đơn vị.

## Quy trình 4 Bước hoàn thành
- **B1 (Model & Seed 5 cấp):** Tạo Model truy vấn đệ quy/nối tiếp bảng CongDong & script 02_seed_5_cap_truong.sql.
- **B2 (Controller 5 cấp):** Viết API lấy danh sách con theo MaCongDongCha và suy ngược đủ 5 cấp từ MaLop của sinh viên.
- **B3 (Tkinter Desktop View):** Dựng Combobox cascading Trường→Khoa→Ngành→Khóa→Lớp và khung Admin thêm/sửa đơn vị.
- **B4 (Demo & KPI):** Test chọn lớp ở Đăng ký & thêm mới 1 lớp ở màn Admin hiện ngay sang danh sách chọn.

**KPI:** Biểu diễn đủ 5 cấp đào tạo chỉ bằng 1 bảng CongDong duy nhất, gọn nhẹ không dư bảng.
