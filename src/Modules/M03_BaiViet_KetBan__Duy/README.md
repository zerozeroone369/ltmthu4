# M3 — Bài viết, Tương tác & Kết bạn

- **Thành viên sở hữu (End-to-End):** Duy (Full-stack Module)
- **Thư mục MVC:** `src/Modules/M03_BaiViet_KetBan__Duy`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `BaiViet`, `BinhLuan`, `TuongTac`, `KetBan`
- **Endpoints / WebSocket dự kiến:**
  - `CRUD /api/m03/posts`
  - `POST /api/m03/posts/{id}/comments`
  - `POST /api/m03/posts/{id}/like`
  - `POST /api/m03/friends/request`
  - `PUT /api/m03/friends/{id}/respond`

## Phạm vi chức năng
Đăng/Sửa/Xóa bài viết theo phạm vi CongDong (kèm đường dẫn TepDinhKem tùy chọn); Bình luận, Thích (chống trùng 1 lượt/người/bài); Tìm bạn học & Kết bạn 2 chiều (KetBan).

## Quy trình 4 Bước hoàn thành
- **B1 (Model 4 bảng MXH):** Viết Model PostgreSQL cho BaiViet, BinhLuan, TuongTac (UNIQUE bài+người) và KetBan.
- **B2 (Controller):** Code API kiểm tra đúng tác giả khi sửa/xóa bài, chống thích trùng, gửi thông báo khi có bình luận/kết bạn.
- **B3 (Tkinter Desktop View):** Dựng khung soạn/sửa bài viết, danh sách bình luận, nút Thích tức thì và tab Kết bạn.
- **B4 (Demo & KPI):** Test trọn luồng từ Tkinter: Đăng bài → Sửa/Xóa → Thích/Bình luận → Tìm & Chấp nhận kết bạn.

**KPI:** Chỉ tác giả sửa/xóa được bài viết của mình, không trùng lượt thích hay lời mời kết bạn.
