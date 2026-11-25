# MẠNG XÃ HỘI PHỤC VỤ ĐỜI SỐNG SINH VIÊN
**Môn học:** Lập trình mạng (Server – Client) • **Mô hình:** Sở hữu trọn gói theo Module (**Modular MVC — End-to-End**)

> **ĐẶC ĐIỂM CỐT LÕI (KHÔNG PHẢI LÀM WEBSITE):**  
> Hệ thống là **ứng dụng mạng Desktop Server – Client** viết bằng **Python 3.11+**: người dùng tương tác trực tiếp trên **App Desktop Python (`Tkinter / ttk`)**, kết nối qua Internet tới **Python Server (`FastAPI + WebSocket`)** deploy trên **Render Cloud** và lưu dữ liệu trên **PostgreSQL (18 bảng tinh gọn chuẩn 3NF)**. Trang `/` trên Render chỉ đóng vai trò **Server Monitor** hiển thị trạng thái kết nối Database, WebSocket & 10 Module MVC cho giảng viên kiểm tra link Cloud.

---

## 0. HƯỚNG DẪN DÙNG FILE `README.md` NÀY ĐỂ TẠO TOÀN BỘ DỰ ÁN MỚI

### Cách 1: Dùng AI trong IDE (Antigravity / Cursor / VS Code Copilot / Claude Code)
1. Tạo thư mục dự án mới (hoặc mở thư mục dự án hiện tại trên nhánh Git riêng).
2. Đặt duy nhất tệp **`README.md`** này vào thư mục gốc dự án.
3. Gửi câu lệnh sau cho AI trong IDE:
   > *"Hãy đọc toàn bộ `README.md` này từ đầu đến cuối để khởi tạo (hoặc tái cấu trúc) trọn vẹn dự án **Mạng xã hội phục vụ đời sống sinh viên** theo đúng cấu trúc Modular MVC Python (`server.py`, `client_app.py`, `src/Shared/`, 10 thư mục `src/Modules/M01..M10` đủ `Models/`, `Views/` Tkinter, `Controllers/`, `README.md`), đúng script CSDL PostgreSQL 18 bảng tinh gọn trong `database/`, đúng `requirements.txt` & `render.yaml`. Nếu dự án đang có code cũ chạy được (đặc biệt Module 1), hãy giữ lại logic đó và đưa vào đúng thư mục `M01`. Hoàn thiện đầy đủ nghiệp vụ theo đặc tả 22 luồng tương tác tác nhân, 10 module và ma trận tích hợp bên dưới."*

### Cách 2: Dựng thủ công theo từng mục
Thực hiện tuần tự từ **Mục 1 → Mục 8**: chạy SQL khởi tạo 18 bảng PostgreSQL → cấu hình `requirements.txt` & `.env` → dựng lõi `src/Shared/` → phân quyền 5 thành viên phát triển song song `src/Modules/M01..M10` → nối Render Blueprint deploy nhánh `main`.

---

## 1. HỒ SƠ CÔNG NGHỆ CHỐT

| Thành phần | Công nghệ sử dụng | Chi tiết kỹ thuật |
| :--- | :--- | :--- |
| **Ngôn ngữ chính** | **Python 3.11+** | Đồng nhất 100% cả phía Client Desktop lẫn Server Cloud |
| **Client (App người dùng)** | **Python `Tkinter` (`ttk`)** + `websockets` + `threading` | App Desktop chạy trên Windows/macOS (KHÔNG phải Web), nhận tin nhắn & thông báo Realtime |
| **Server Cloud** | **Python `FastAPI` + `WebSocket` (`uvicorn`)** | API JSON & kênh `/ws`, xác thực PyJWT với bảng `"NguoiDung"`, trang Monitor tại `/`, `/health`, `/docs` |
| **Cơ sở dữ liệu** | **PostgreSQL 15 / 16 (18 Bảng 3NF tinh gọn)** | **`18` bảng thực sự cần thiết**, `37` khóa ngoại FK, đầy đủ `UNIQUE`, `CHECK`, `INDEX`; driver **`psycopg[binary]`** |
| **Bảo mật & Upload** | `passlib[bcrypt]`, `PyJWT`, `python-multipart` | Mã hóa mật khẩu một chiều; kiểm tra định dạng & dung lượng `<20MB` khi tải tài liệu |
| **Cloud & GitHub** | **Render Cloud (Free Plan)** + **GitHub Modular MVC** | Render Blueprint (`render.yaml`) auto-build & deploy từ nhánh `main` của GitHub |

---

## 2. KIẾN TRÚC TƯƠNG TÁC & 3 VAI TRÒ TÁC NHÂN

Toàn bộ các quy trình chỉ mô tả **cách các tác nhân người dùng tương tác trực tiếp với ứng dụng** và kết quả nhận lại trên màn hình:

1. **Sinh viên (Tác nhân chính — 16 luồng):** Đăng ký theo lớp, Đăng nhập/Đăng xuất, Đổi/Quên mật khẩu OTP, Sửa hồ sơ & Đổi lớp, Quyền riêng tư & Chặn, Tìm & Kết bạn, Xem Bảng tin & Thông báo, Đăng/Sửa/Xóa bài, Bình luận & Thích, Nhắn tin 1-1 & Chat nhóm, Chia sẻ/Tải về & Chấm sao tài liệu, Hỏi đáp Q&A & Upvote, Xin vào nhóm học, Xem tin Campus, Báo cáo vi phạm.
2. **Trưởng nhóm học tập (Vai trò của Sinh viên lập nhóm — 2 luồng):** Tạo nhóm học tập, Duyệt/Từ chối đơn xin gia nhập theo sức chứa, Điều chỉnh sĩ số, Chuyển quyền Trưởng nhóm khi rời nhóm.
3. **Quản trị viên / Admin (Tác nhân quản trị — 4 luồng):** Đăng & quản lý tin Campus, Kiểm duyệt báo cáo vi phạm (`BaoCaoViPham`), Quản lý cây Cộng đồng 5 cấp (`CongDong`), Quản trị tài khoản & vai trò (`NguoiDung`).

### Tổng hợp 24 Sơ đồ Tương tác (2 Tổng quan + 22 Luồng Tác nhân)

| Mã | Tên Luồng Tương tác | Mô tả cách Tác nhân tương tác |
| :-: | :--- | :--- |
| **00A** (`wf0`) | LUỒNG TỔNG HỢP TƯƠNG TÁC CỦA 3 VAI TRÒ TÁC NHÂN | Cách Sinh viên, Trưởng nhóm học tập và Quản trị viên tương tác với ứng dụng từ đầu tới cuối. |
| **00B** (`wf0_actors`) | MA TRẬN TÁC NHÂN & PHÂN BỔ 22 LUỒNG TƯƠNG TÁC | Mối tương tác chéo giữa 3 vai trò người dùng qua Hệ thống và danh sách 22 quy trình nghiệp vụ. |
| **01** (`wf1`) | ĐĂNG KÝ TÀI KHOẢN & THAM GIA CỘNG ĐỒNG | Sinh viên nhập thông tin cá nhân, chọn lớp sinh hoạt trong cây 5 cấp để mở tài khoản và vào cộng đồng học tập. |
| **02** (`wf2`) | ĐĂNG NHẬP VÀO HỆ THỐNG | Sinh viên hoặc Quản trị viên nhập thông tin tài khoản để truy cập vào màn hình chức năng phù hợp vai trò. |
| **03** (`wf_pw`) | ĐỔI MẬT KHẨU | Sinh viên tự thay đổi mật khẩu hiện tại trong mục Tài khoản để bảo vệ quyền truy cập cá nhân. |
| **04** (`wf_forgot_pw`) | QUÊN MẬT KHẨU & ĐẶT LẠI MẬT KHẨU | Sinh viên nhập email đã đăng ký, nhận mã xác thực 6 số qua email và đặt lại mật khẩu mới. |
| **05** (`wf_logout`) | ĐĂNG XUẤT KHỎI ỨNG DỤNG | Sinh viên hoặc Quản trị viên chủ động kết thúc phiên làm việc để bảo vệ tài khoản khi rời máy tính. |
| **06** (`wf_profile`) | CẬP NHẬT HỒ SƠ & CHUYỂN LỚP | Sinh viên cập nhật thông tin cá nhân, ảnh đại diện hoặc chuyển lớp học để tham gia đúng cộng đồng mới. |
| **07** (`wf_privacy`) | CÀI ĐẶT QUYỀN RIÊNG TƯ & CHẶN LIÊN LẠC | Sinh viên tùy chỉnh ai được xem SĐT, Email, bài viết hoặc thêm/gỡ chặn người làm phiền. |
| **08** (`wf_friend`) | TÌM BẠN HỌC & KẾT BẠN | Sinh viên tìm kiếm bạn học theo tên, lớp hoặc MSSV, gửi lời mời kết bạn và bên nhận đồng ý hoặc từ chối. |
| **09** (`wf_feed_notif`) | XEM BẢNG TIN & ĐỌC THÔNG BÁO | Sinh viên duyệt bảng tin theo cộng đồng/chủ đề học tập và bấm chuông xem các thông báo mới. |
| **10** (`wf3`) | ĐĂNG BÀI VIẾT MỚI LÊN CỘNG ĐỒNG | Sinh viên soạn nội dung, chọn phạm vi cộng đồng, đính kèm tệp nếu cần và đăng lên Bảng tin. |
| **11** (`wf_post_edit`) | CHỈNH SỬA & XÓA BÀI VIẾT CỦA MÌNH | Sinh viên tác giả chỉnh sửa lại nội dung hoặc xóa bài viết của chính mình trên Bảng tin. |
| **12** (`wf_cmt`) | BÌNH LUẬN & THÍCH BÀI VIẾT | Sinh viên nhấn nút Thích hoặc viết bình luận trao đổi bên dưới bài viết và tác giả nhận thông báo ngay. |
| **13** (`wf_chat`) | NHẮN TIN 1-1 & CHAT NHÓM HỌC TẬP | Sinh viên chọn bạn bè hoặc nhóm học để nhắn tin hai chiều và nhận tin nhắn đến tức thì. |
| **14** (`wf4`) | CHIA SẺ (TẢI LÊN) & TẢI VỀ TÀI LIỆU HỌC TẬP | Sinh viên tải tài liệu ôn thi/slide lên theo môn học hoặc tìm và tải tài liệu của bạn bè về máy. |
| **15** (`wf_doc_review`) | TÌM KIẾM & ĐÁNH GIÁ TÀI LIỆU (1–5 SAO) | Sinh viên lọc tìm tài liệu theo môn học/từ khóa và chấm điểm 1–5 sao kèm nhận xét chất lượng. |
| **16** (`wf6`) | HỎI ĐÁP HỌC THUẬT (Q&A), UPVOTE & CHỐT ĐÁP ÁN | Sinh viên đặt câu hỏi theo môn học, bạn bè vào trả lời và upvote hữu ích; chủ câu hỏi chọn đáp án đúng. |
| **17** (`wf5`) | TẠO NHÓM HỌC TẬP & DUYỆT THÀNH VIÊN | Sinh viên tạo nhóm học mới để trở thành Trưởng nhóm; bạn khác gửi đơn xin vào và Trưởng nhóm duyệt theo sĩ số. |
| **18** (`wf_leave`) | RỜI NHÓM, CẬP NHẬT SĨ SỐ & CHUYỂN TRƯỞNG NHÓM | Thành viên rời nhóm bình thường; riêng Trưởng nhóm bắt buộc bàn giao quyền cho thành viên khác trước khi rời. |
| **19** (`wf_campus`) | XEM & ĐĂNG TIN TỨC CAMPUS | Quản trị viên đăng tin sự kiện, học bổng, việc làm theo phạm vi Trường/Khoa; Sinh viên mở tab Campus để xem và lọc tin. |
| **20** (`wf7`) | BÁO CÁO VI PHẠM & KIỂM DUYỆT ADMIN | Sinh viên gửi báo cáo nội dung xấu; Quản trị viên vào danh sách kiểm duyệt để xem xét và ra quyết định xử lý. |
| **21** (`wf_edu`) | QUẢN LÝ CÂY CỘNG ĐỒNG ĐÀO TẠO 5 CẤP | Quản trị viên thêm mới, chỉnh sửa hoặc tạm ngưng các đơn vị Trường → Khoa → Ngành → Khóa → Lớp trên cây cộng đồng. |
| **22** (`wf_admin_user`) | QUẢN TRỊ TÀI KHOẢN & PHÂN QUYỀN (ADMIN) | Quản trị viên tìm kiếm người dùng để cấp/thu hồi quyền Admin hoặc khóa, mở khóa tài khoản vi phạm. |

---

## 3. PHÂN CÔNG 5 THÀNH VIÊN & CÂY THƯ MỤC GITHUB (MODULAR MVC)

- **Nguyên tắc sở hữu End-to-End:** Mỗi thành viên làm chủ trọn vẹn **02 Module** từ DB (`Models/`) → Server (`Controllers/`) → Desktop UI (`Views/` Tkinter) → Demo & Vấn đáp.
- **Link Cloud (Render):** *(Dán sau khi deploy: `https://mxh-sinh-vien-ltm.onrender.com`)*

| STT | Thành viên & Vai trò | GitHub Account | Module | Thư mục MVC phụ trách trên GitHub | Bảng PostgreSQL sở hữu (18 Bảng) |
| :-: | :--- | :--- | :-: | :--- | :--- |
| 1 | **Nguyễn Ngô Tú Anh** (*Leader & Core Auth/Admin*) | `@github-username` | `M1`, `M10` | `src/Modules/M01_Auth_TaiKhoan__TuAnh`<br>`src/Modules/M10_QuanTri_KiemDuyet__TuAnh` | `NguoiDung, BaoCaoViPham` |
| 2 | **Duy** (*Full-stack Module*) | `@github-username` | `M2`, `M3` | `src/Modules/M02_CongDong_5Cap__Duy`<br>`src/Modules/M03_BaiViet_KetBan__Duy` | `CongDong, BaiViet, BinhLuan, TuongTac, KetBan` |
| 3 | **Huy** (*Full-stack Module*) | `@github-username` | `M4`, `M5` | `src/Modules/M04_TaiLieu_TepTin__Huy`<br>`src/Modules/M05_HoiDap_QA__Huy` | `MonHoc, TaiLieu, DanhGiaTaiLieu, CauHoi, CauTraLoi, BinhChonCauTraLoi` |
| 4 | **Bảo** (*Full-stack Module*) | `@github-username` | `M6`, `M7` | `src/Modules/M06_NhomHoc__Bao`<br>`src/Modules/M07_Campus__Bao` | `NhomHoc, ThanhVienNhom, TinTruong` |
| 5 | **Thái** (*Full-stack & UI Lead*) | `@github-username` | `M8`, `M9` | `src/Modules/M08_BangTin_RiengTu__Thai`<br>`src/Modules/M09_Chat_ThongBao_Realtime__Thai` | `TinNhan, ThongBao` |

### Cây thư mục chuẩn của Dự án

```text
mxh-sinh-vien-ltm/
├── README.md                                  # Tài liệu tổng hợp & đặc tả thực thi toàn dự án
├── THUC_HIEN_DU_AN_MXH_SINH_VIEN.md           # Kế hoạch thực thi theo 4 giai đoạn
├── requirements.txt                           # Thư viện Python cho Server & Desktop Client
├── render.yaml                                # Cấu hình tự động deploy Python + PostgreSQL trên Render
├── .env.example                               # Mẫu biến môi trường (DATABASE_URL, JWT_SECRET, SERVER_URL)
├── .gitignore
├── server.py                                  # Máy chủ Python FastAPI + WebSocket /ws + Trang Monitor /
├── client_app.py                              # App Desktop Python Tkinter kết nối lên Render Server
├── database/
│   ├── 01_schema_18_tables_postgres.sql       # Script tạo 18 bảng PostgreSQL tinh gọn (37 FK, UNIQUE, CHECK, Index)
│   └── 02_seed_5_cap_truong.sql               # Script dữ liệu mẫu cây CongDong 5 cấp + 3 MonHoc
└── src/
    ├── __init__.py
    ├── Shared/
    │   ├── config/db.py                       # Kết nối PostgreSQL psycopg (get_conn, check_db_health)
    │   └── middlewares/
    │       ├── auth_middleware.py             # verify_token (PyJWT + NguoiDung) & require_admin
    │       └── realtime_helper.py             # ConnectionManager (/ws) & send_notification()
    └── Modules/                               # MỖI MODULE ĐỦ 3 THƯ MỤC MVC: Controllers/ Models/ Views/
        ├── M01_Auth_TaiKhoan__TuAnh/          (Controllers/m01_controller.py, Models/m01_model.py, Views/m01_view.py, README.md)
        ├── M02_CongDong_5Cap__Duy/            (Controllers/m02_controller.py, Models/m02_model.py, Views/m02_view.py, README.md)
        ├── M03_BaiViet_KetBan__Duy/           (Controllers/m03_controller.py, Models/m03_model.py, Views/m03_view.py, README.md)
        ├── M04_TaiLieu_TepTin__Huy/           (Controllers/m04_controller.py, Models/m04_model.py, Views/m04_view.py, README.md)
        ├── M05_HoiDap_QA__Huy/                (Controllers/m05_controller.py, Models/m05_model.py, Views/m05_view.py, README.md)
        ├── M06_NhomHoc__Bao/                  (Controllers/m06_controller.py, Models/m06_model.py, Views/m06_view.py, README.md)
        ├── M07_Campus__Bao/                   (Controllers/m07_controller.py, Models/m07_model.py, Views/m07_view.py, README.md)
        ├── M08_BangTin_RiengTu__Thai/         (Controllers/m08_controller.py, Models/m08_model.py, Views/m08_view.py, README.md)
        ├── M09_Chat_ThongBao_Realtime__Thai/  (Controllers/m09_controller.py, Models/m09_model.py, Views/m09_view.py, README.md)
        └── M10_QuanTri_KiemDuyet__TuAnh/      (Controllers/m10_controller.py, Models/m10_model.py, Views/m10_view.py, README.md)
```

---

## 4. CƠ SỞ DỮ LIỆU POSTGRESQL 18 BẢNG TINH GỌN (CHUẨN 3NF)

- **Nguyên tắc tinh gọn:** Chỉ giữ lại **`18` bảng thực sự cần tồn tại** cho các tính năng nghiệp vụ (`37` khóa ngoại `FOREIGN KEY`, đầy đủ `UNIQUE`, `CHECK` & `INDEX`). Đã loại bỏ/hợp nhất các bảng rườm rà không cần thiết (gộp 5 cấp trường thành cây tự tham chiếu `CongDong`, gộp tùy chọn riêng tư & OTP vào `NguoiDung`, gộp chặn người dùng vào `KetBan`, gộp đơn chờ vào `ThanhVienNhom`, gộp kết quả kiểm duyệt vào `BaoCaoViPham`, bỏ các bảng log/queue/lịch sử trung gian).

### 4.1. Danh mục 18 Bảng PostgreSQL

| # | Tên Bảng | Phân hệ | Vai trò nghiệp vụ | Quan hệ chính |
| :-: | :--- | :--- | :--- | :--- |
| 1 | `"CongDong"` | Đào tạo & Cộng đồng | Không gian cộng đồng và cây đào tạo 5 cấp (Trường → Khoa → Ngành → Khóa → Lớp) | Tự tham chiếu MaCongDongCha (5 cấp); 1–N với NguoiDung, BaiViet, TaiLieu, CauHoi, NhomHoc, TinTruong |
| 2 | `"NguoiDung"` | Tài khoản & Kết bạn | Tài khoản Sinh viên & Quản trị viên (kèm vai trò, lớp, tùy chọn riêng tư & OTP quên MK) | N–1 với CongDong (MaLop); 1–N với KetBan, BaiViet, TinNhan, TaiLieu, CauHoi, NhomHoc, ThongBao... |
| 3 | `"KetBan"` | Tài khoản & Kết bạn | Quan hệ bạn bè (chờ duyệt / bạn bè) và chặn liên lạc giữa sinh viên | N–1 với NguoiDung (hai phía người gửi và người nhận) |
| 4 | `"BaiViet"` | Bài viết & Nhắn tin | Bài đăng chia sẻ kiến thức, thảo luận trên bảng tin cộng đồng (có thể đính kèm tệp) | N–1 với NguoiDung, CongDong; 1–N với BinhLuan, TuongTac |
| 5 | `"BinhLuan"` | Bài viết & Nhắn tin | Bình luận trao đổi dưới từng bài viết | N–1 với BaiViet, NguoiDung |
| 6 | `"TuongTac"` | Bài viết & Nhắn tin | Lượt thích (Like) bài viết — mỗi sinh viên tối đa 1 lượt trên mỗi bài | N–1 với BaiViet, NguoiDung |
| 7 | `"TinNhan"` | Bài viết & Nhắn tin | Tin nhắn trò chuyện trực tiếp 1-1 và chat nhóm học tập | N–1 với NguoiDung (gửi/nhận) và NhomHoc (chat nhóm) |
| 8 | `"MonHoc"` | Tài liệu & Môn học | Danh mục môn học phục vụ chia sẻ tài liệu, hỏi đáp Q&A và lập nhóm học | N–1 với CongDong (Trường); 1–N với TaiLieu, CauHoi, NhomHoc |
| 9 | `"TaiLieu"` | Tài liệu & Môn học | Tài liệu học tập, đề thi, slide chia sẻ theo môn học (kèm thông tin tệp & thống kê) | N–1 với NguoiDung, MonHoc, CongDong; 1–N với DanhGiaTaiLieu |
| 10 | `"DanhGiaTaiLieu"` | Tài liệu & Môn học | Đánh giá sao (1–5★) và nhận xét chất lượng tài liệu học tập | N–N giữa TaiLieu và NguoiDung |
| 11 | `"CauHoi"` | Hỏi đáp Q&A | Câu hỏi thảo luận bài tập, đồ án theo môn học (kèm thẻ từ khóa) | N–1 với NguoiDung, MonHoc, CongDong; 1–N với CauTraLoi |
| 12 | `"CauTraLoi"` | Hỏi đáp Q&A | Câu trả lời giải đáp cho câu hỏi trên diễn đàn Q&A | N–1 với CauHoi, NguoiDung; 1–N với BinhChonCauTraLoi |
| 13 | `"BinhChonCauTraLoi"` | Hỏi đáp Q&A | Lượt upvote cho câu trả lời — chống một người vote nhiều lần | N–1 với CauTraLoi, NguoiDung |
| 14 | `"NhomHoc"` | Nhóm học tập | Nhóm học tập theo môn học (do sinh viên khởi tạo và làm Trưởng nhóm) | N–1 với MonHoc, CongDong, NguoiDung (Trưởng nhóm); 1–N với ThanhVienNhom, TinNhan |
| 15 | `"ThanhVienNhom"` | Nhóm học tập | Danh sách thành viên chính thức và đơn xin gia nhập nhóm học | N–N giữa NhomHoc và NguoiDung |
| 16 | `"TinTruong"` | Campus & Kiểm duyệt | Tin tức Campus từ Quản trị viên: Sự kiện, Học bổng, CLB, Thực tập | N–1 với NguoiDung (Admin), CongDong |
| 17 | `"ThongBao"` | Campus & Kiểm duyệt | Hộp thư thông báo gửi tới sinh viên khi có tương tác hoặc kết quả duyệt | N–1 với NguoiDung (người nhận & người tạo sự kiện) |
| 18 | `"BaoCaoViPham"` | Campus & Kiểm duyệt | Báo cáo nội dung vi phạm từ sinh viên và kết quả xử lý của Quản trị viên | N–1 với NguoiDung (người báo cáo & Admin xử lý) |

### 4.2. Script khởi tạo đầy đủ (`database/01_schema_18_tables_postgres.sql`)

```sql
-- =========================================================================
-- CSDL POSTGRESQL 15/16 TINH GỌN (18 BẢNG CỐT LÕI - CHUẨN 3NF)
-- Chỉ giữ các bảng thật sự cần thiết cho nghiệp vụ Mạng xã hội Sinh viên
-- =========================================================================

-- Bảng: CongDong (Không gian cộng đồng và cây đào tạo 5 cấp (Trường → Khoa → Ngành → Khóa → Lớp))
CREATE TABLE IF NOT EXISTS "CongDong" (
    "MaCongDong" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaCongDongCha" BIGINT NULL,
    "KyHieu" VARCHAR(30) NULL,
    "TenCongDong" VARCHAR(200) NOT NULL,
    "CapDo" VARCHAR(20) NOT NULL,
    "NamBatDau" INT NULL,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'DangHoatDong',
    CONSTRAINT "PK_CongDong" PRIMARY KEY ("MaCongDong")
);

-- Bảng: NguoiDung (Tài khoản Sinh viên & Quản trị viên (kèm vai trò, lớp, tùy chọn riêng tư & OTP quên MK))
CREATE TABLE IF NOT EXISTS "NguoiDung" (
    "MaNguoiDung" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaLop" BIGINT NULL,
    "VaiTro" VARCHAR(20) NOT NULL DEFAULT 'SinhVien',
    "MaSinhVien" VARCHAR(30) NULL,
    "Email" VARCHAR(254) NOT NULL,
    "MatKhauHash" VARCHAR(255) NOT NULL,
    "HoTen" VARCHAR(100) NOT NULL,
    "SoDienThoai" VARCHAR(20) NULL,
    "AnhDaiDien" VARCHAR(255) NULL,
    "GioiThieu" VARCHAR(500) NULL,
    "CaiDatRiengTu" TEXT NOT NULL DEFAULT '{"hienSdt":"BanBe","hienEmail":"CongDong"}',
    "MaOTP" VARCHAR(10) NULL,
    "HanOTP" TIMESTAMPTZ NULL,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'HoatDong',
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "NgayCapNhat" TIMESTAMPTZ NULL,
    CONSTRAINT "PK_NguoiDung" PRIMARY KEY ("MaNguoiDung")
);

-- Bảng: KetBan (Quan hệ bạn bè (chờ duyệt / bạn bè) và chặn liên lạc giữa sinh viên)
CREATE TABLE IF NOT EXISTS "KetBan" (
    "MaKetBan" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaNguoiGui" BIGINT NOT NULL,
    "MaNguoiNhan" BIGINT NOT NULL,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'ChoDuyet',
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "NgayCapNhat" TIMESTAMPTZ NULL,
    CONSTRAINT "PK_KetBan" PRIMARY KEY ("MaKetBan")
);

-- Bảng: BaiViet (Bài đăng chia sẻ kiến thức, thảo luận trên bảng tin cộng đồng (có thể đính kèm tệp))
CREATE TABLE IF NOT EXISTS "BaiViet" (
    "MaBaiViet" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "MaCongDong" BIGINT NOT NULL,
    "DanhMuc" VARCHAR(30) NOT NULL DEFAULT 'HocTap',
    "NoiDung" TEXT NOT NULL,
    "TepDinhKem" VARCHAR(500) NULL,
    "SoLuotThich" INT NOT NULL DEFAULT 0,
    "SoBinhLuan" INT NOT NULL DEFAULT 0,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'HienThi',
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "NgayCapNhat" TIMESTAMPTZ NULL,
    CONSTRAINT "PK_BaiViet" PRIMARY KEY ("MaBaiViet")
);

-- Bảng: BinhLuan (Bình luận trao đổi dưới từng bài viết)
CREATE TABLE IF NOT EXISTS "BinhLuan" (
    "MaBinhLuan" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaBaiViet" BIGINT NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "NoiDung" VARCHAR(2000) NOT NULL,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'HienThi',
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_BinhLuan" PRIMARY KEY ("MaBinhLuan")
);

-- Bảng: TuongTac (Lượt thích (Like) bài viết — mỗi sinh viên tối đa 1 lượt trên mỗi bài)
CREATE TABLE IF NOT EXISTS "TuongTac" (
    "MaTuongTac" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaBaiViet" BIGINT NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "LoaiTuongTac" VARCHAR(20) NOT NULL DEFAULT 'Thich',
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_TuongTac" PRIMARY KEY ("MaTuongTac")
);

-- Bảng: TinNhan (Tin nhắn trò chuyện trực tiếp 1-1 và chat nhóm học tập)
CREATE TABLE IF NOT EXISTS "TinNhan" (
    "MaTinNhan" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaNguoiGui" BIGINT NOT NULL,
    "MaNguoiNhan" BIGINT NULL,
    "MaNhomHoc" BIGINT NULL,
    "NoiDung" TEXT NOT NULL,
    "DaDoc" BOOLEAN NOT NULL DEFAULT FALSE,
    "ThoiGianGui" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_TinNhan" PRIMARY KEY ("MaTinNhan")
);

-- Bảng: MonHoc (Danh mục môn học phục vụ chia sẻ tài liệu, hỏi đáp Q&A và lập nhóm học)
CREATE TABLE IF NOT EXISTS "MonHoc" (
    "MaMonHoc" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaTruong" BIGINT NOT NULL,
    "KyHieuMonHoc" VARCHAR(30) NOT NULL,
    "TenMonHoc" VARCHAR(200) NOT NULL,
    "SoTinChi" INT NOT NULL DEFAULT 3,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'DangMo',
    CONSTRAINT "PK_MonHoc" PRIMARY KEY ("MaMonHoc")
);

-- Bảng: TaiLieu (Tài liệu học tập, đề thi, slide chia sẻ theo môn học (kèm thông tin tệp & thống kê))
CREATE TABLE IF NOT EXISTS "TaiLieu" (
    "MaTaiLieu" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "MaMonHoc" BIGINT NOT NULL,
    "MaCongDong" BIGINT NOT NULL,
    "TieuDe" VARCHAR(255) NOT NULL,
    "MoTa" VARCHAR(1000) NOT NULL DEFAULT '',
    "TenTep" VARCHAR(255) NOT NULL,
    "DuongDanTep" VARCHAR(500) NOT NULL,
    "KichThuocByte" BIGINT NOT NULL,
    "SoLuotTai" INT NOT NULL DEFAULT 0,
    "DiemDanhGiaTB" NUMERIC(3,2) NOT NULL DEFAULT 0.00,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'CongBo',
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_TaiLieu" PRIMARY KEY ("MaTaiLieu")
);

-- Bảng: DanhGiaTaiLieu (Đánh giá sao (1–5★) và nhận xét chất lượng tài liệu học tập)
CREATE TABLE IF NOT EXISTS "DanhGiaTaiLieu" (
    "MaTaiLieu" BIGINT NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "Diem" INT NOT NULL,
    "NhanXet" VARCHAR(500) NOT NULL DEFAULT '',
    "NgayDanhGia" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_DanhGiaTaiLieu" PRIMARY KEY ("MaTaiLieu", "MaNguoiDung")
);

-- Bảng: CauHoi (Câu hỏi thảo luận bài tập, đồ án theo môn học (kèm thẻ từ khóa))
CREATE TABLE IF NOT EXISTS "CauHoi" (
    "MaCauHoi" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "MaMonHoc" BIGINT NOT NULL,
    "MaCongDong" BIGINT NOT NULL,
    "TieuDe" VARCHAR(255) NOT NULL,
    "NoiDung" TEXT NOT NULL,
    "TheTuKhoa" VARCHAR(200) NULL,
    "DaGiaiQuyet" BOOLEAN NOT NULL DEFAULT FALSE,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'DangMo',
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_CauHoi" PRIMARY KEY ("MaCauHoi")
);

-- Bảng: CauTraLoi (Câu trả lời giải đáp cho câu hỏi trên diễn đàn Q&A)
CREATE TABLE IF NOT EXISTS "CauTraLoi" (
    "MaCauTraLoi" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaCauHoi" BIGINT NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "NoiDung" TEXT NOT NULL,
    "SoUpvote" INT NOT NULL DEFAULT 0,
    "LaCauTraLoiDung" BOOLEAN NOT NULL DEFAULT FALSE,
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_CauTraLoi" PRIMARY KEY ("MaCauTraLoi")
);

-- Bảng: BinhChonCauTraLoi (Lượt upvote cho câu trả lời — chống một người vote nhiều lần)
CREATE TABLE IF NOT EXISTS "BinhChonCauTraLoi" (
    "MaBinhChon" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaCauTraLoi" BIGINT NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_BinhChonCauTraLoi" PRIMARY KEY ("MaBinhChon")
);

-- Bảng: NhomHoc (Nhóm học tập theo môn học (do sinh viên khởi tạo và làm Trưởng nhóm))
CREATE TABLE IF NOT EXISTS "NhomHoc" (
    "MaNhomHoc" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaMonHoc" BIGINT NOT NULL,
    "MaCongDong" BIGINT NOT NULL,
    "MaTruongNhom" BIGINT NOT NULL,
    "TenNhom" VARCHAR(200) NOT NULL,
    "MucTieu" VARCHAR(500) NOT NULL DEFAULT '',
    "SoThanhVienHienTai" INT NOT NULL DEFAULT 1,
    "SoThanhVienToiDa" INT NOT NULL DEFAULT 10,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'DangTuyen',
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_NhomHoc" PRIMARY KEY ("MaNhomHoc")
);

-- Bảng: ThanhVienNhom (Danh sách thành viên chính thức và đơn xin gia nhập nhóm học)
CREATE TABLE IF NOT EXISTS "ThanhVienNhom" (
    "MaNhomHoc" BIGINT NOT NULL,
    "MaNguoiDung" BIGINT NOT NULL,
    "VaiTro" VARCHAR(20) NOT NULL DEFAULT 'ThanhVien',
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'ChoDuyet',
    "LoiNhan" VARCHAR(500) NULL,
    "NgayThamGia" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_ThanhVienNhom" PRIMARY KEY ("MaNhomHoc", "MaNguoiDung")
);

-- Bảng: TinTruong (Tin tức Campus từ Quản trị viên: Sự kiện, Học bổng, CLB, Thực tập)
CREATE TABLE IF NOT EXISTS "TinTruong" (
    "MaTinTruong" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaQuanTriVien" BIGINT NOT NULL,
    "MaCongDong" BIGINT NOT NULL,
    "DanhMuc" VARCHAR(30) NOT NULL,
    "TieuDe" VARCHAR(255) NOT NULL,
    "NoiDung" TEXT NOT NULL,
    "NgayHetHan" TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 days'),
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'CongBo',
    "NgayDang" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_TinTruong" PRIMARY KEY ("MaTinTruong")
);

-- Bảng: ThongBao (Hộp thư thông báo gửi tới sinh viên khi có tương tác hoặc kết quả duyệt)
CREATE TABLE IF NOT EXISTS "ThongBao" (
    "MaThongBao" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaNguoiNhan" BIGINT NOT NULL,
    "MaNguoiThucHien" BIGINT NULL,
    "LoaiThongBao" VARCHAR(30) NOT NULL,
    "NoiDung" VARCHAR(500) NOT NULL,
    "LienKet" VARCHAR(255) NULL,
    "DaDoc" BOOLEAN NOT NULL DEFAULT FALSE,
    "NgayTao" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "PK_ThongBao" PRIMARY KEY ("MaThongBao")
);

-- Bảng: BaoCaoViPham (Báo cáo nội dung vi phạm từ sinh viên và kết quả xử lý của Quản trị viên)
CREATE TABLE IF NOT EXISTS "BaoCaoViPham" (
    "MaBaoCao" BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    "MaNguoiBaoCao" BIGINT NOT NULL,
    "MaAdminXuLy" BIGINT NULL,
    "LoaiNoiDung" VARCHAR(30) NOT NULL,
    "IdNoiDung" BIGINT NOT NULL,
    "LyDo" VARCHAR(100) NOT NULL,
    "ChiTiet" VARCHAR(1000) NULL,
    "TrangThai" VARCHAR(20) NOT NULL DEFAULT 'ChoDuyet',
    "QuyetDinh" VARCHAR(30) NULL,
    "GhiChuXuLy" VARCHAR(500) NULL,
    "NgayGui" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "NgayXuLy" TIMESTAMPTZ NULL,
    CONSTRAINT "PK_BaoCaoViPham" PRIMARY KEY ("MaBaoCao")
);

-- =========================================================================
-- PHẦN 2: KHÓA NGOẠI (37 FOREIGN KEYS)
-- =========================================================================
ALTER TABLE "CongDong" DROP CONSTRAINT IF EXISTS "FK_CongDong_MaCongDongCha_CongDong";
ALTER TABLE "CongDong" ADD CONSTRAINT "FK_CongDong_MaCongDongCha_CongDong" FOREIGN KEY ("MaCongDongCha") REFERENCES "CongDong"("MaCongDong");
ALTER TABLE "NguoiDung" DROP CONSTRAINT IF EXISTS "FK_NguoiDung_MaLop_CongDong";
ALTER TABLE "NguoiDung" ADD CONSTRAINT "FK_NguoiDung_MaLop_CongDong" FOREIGN KEY ("MaLop") REFERENCES "CongDong"("MaCongDong");
ALTER TABLE "KetBan" DROP CONSTRAINT IF EXISTS "FK_KetBan_MaNguoiGui_NguoiDung";
ALTER TABLE "KetBan" ADD CONSTRAINT "FK_KetBan_MaNguoiGui_NguoiDung" FOREIGN KEY ("MaNguoiGui") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "KetBan" DROP CONSTRAINT IF EXISTS "FK_KetBan_MaNguoiNhan_NguoiDung";
ALTER TABLE "KetBan" ADD CONSTRAINT "FK_KetBan_MaNguoiNhan_NguoiDung" FOREIGN KEY ("MaNguoiNhan") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "BaiViet" DROP CONSTRAINT IF EXISTS "FK_BaiViet_MaNguoiDung_NguoiDung";
ALTER TABLE "BaiViet" ADD CONSTRAINT "FK_BaiViet_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "BaiViet" DROP CONSTRAINT IF EXISTS "FK_BaiViet_MaCongDong_CongDong";
ALTER TABLE "BaiViet" ADD CONSTRAINT "FK_BaiViet_MaCongDong_CongDong" FOREIGN KEY ("MaCongDong") REFERENCES "CongDong"("MaCongDong");
ALTER TABLE "BinhLuan" DROP CONSTRAINT IF EXISTS "FK_BinhLuan_MaBaiViet_BaiViet";
ALTER TABLE "BinhLuan" ADD CONSTRAINT "FK_BinhLuan_MaBaiViet_BaiViet" FOREIGN KEY ("MaBaiViet") REFERENCES "BaiViet"("MaBaiViet");
ALTER TABLE "BinhLuan" DROP CONSTRAINT IF EXISTS "FK_BinhLuan_MaNguoiDung_NguoiDung";
ALTER TABLE "BinhLuan" ADD CONSTRAINT "FK_BinhLuan_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "TuongTac" DROP CONSTRAINT IF EXISTS "FK_TuongTac_MaBaiViet_BaiViet";
ALTER TABLE "TuongTac" ADD CONSTRAINT "FK_TuongTac_MaBaiViet_BaiViet" FOREIGN KEY ("MaBaiViet") REFERENCES "BaiViet"("MaBaiViet");
ALTER TABLE "TuongTac" DROP CONSTRAINT IF EXISTS "FK_TuongTac_MaNguoiDung_NguoiDung";
ALTER TABLE "TuongTac" ADD CONSTRAINT "FK_TuongTac_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "TinNhan" DROP CONSTRAINT IF EXISTS "FK_TinNhan_MaNguoiGui_NguoiDung";
ALTER TABLE "TinNhan" ADD CONSTRAINT "FK_TinNhan_MaNguoiGui_NguoiDung" FOREIGN KEY ("MaNguoiGui") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "TinNhan" DROP CONSTRAINT IF EXISTS "FK_TinNhan_MaNguoiNhan_NguoiDung";
ALTER TABLE "TinNhan" ADD CONSTRAINT "FK_TinNhan_MaNguoiNhan_NguoiDung" FOREIGN KEY ("MaNguoiNhan") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "TinNhan" DROP CONSTRAINT IF EXISTS "FK_TinNhan_MaNhomHoc_NhomHoc";
ALTER TABLE "TinNhan" ADD CONSTRAINT "FK_TinNhan_MaNhomHoc_NhomHoc" FOREIGN KEY ("MaNhomHoc") REFERENCES "NhomHoc"("MaNhomHoc");
ALTER TABLE "MonHoc" DROP CONSTRAINT IF EXISTS "FK_MonHoc_MaTruong_CongDong";
ALTER TABLE "MonHoc" ADD CONSTRAINT "FK_MonHoc_MaTruong_CongDong" FOREIGN KEY ("MaTruong") REFERENCES "CongDong"("MaCongDong");
ALTER TABLE "TaiLieu" DROP CONSTRAINT IF EXISTS "FK_TaiLieu_MaNguoiDung_NguoiDung";
ALTER TABLE "TaiLieu" ADD CONSTRAINT "FK_TaiLieu_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "TaiLieu" DROP CONSTRAINT IF EXISTS "FK_TaiLieu_MaMonHoc_MonHoc";
ALTER TABLE "TaiLieu" ADD CONSTRAINT "FK_TaiLieu_MaMonHoc_MonHoc" FOREIGN KEY ("MaMonHoc") REFERENCES "MonHoc"("MaMonHoc");
ALTER TABLE "TaiLieu" DROP CONSTRAINT IF EXISTS "FK_TaiLieu_MaCongDong_CongDong";
ALTER TABLE "TaiLieu" ADD CONSTRAINT "FK_TaiLieu_MaCongDong_CongDong" FOREIGN KEY ("MaCongDong") REFERENCES "CongDong"("MaCongDong");
ALTER TABLE "DanhGiaTaiLieu" DROP CONSTRAINT IF EXISTS "FK_DanhGiaTaiLieu_MaTaiLieu_TaiLieu";
ALTER TABLE "DanhGiaTaiLieu" ADD CONSTRAINT "FK_DanhGiaTaiLieu_MaTaiLieu_TaiLieu" FOREIGN KEY ("MaTaiLieu") REFERENCES "TaiLieu"("MaTaiLieu");
ALTER TABLE "DanhGiaTaiLieu" DROP CONSTRAINT IF EXISTS "FK_DanhGiaTaiLieu_MaNguoiDung_NguoiDung";
ALTER TABLE "DanhGiaTaiLieu" ADD CONSTRAINT "FK_DanhGiaTaiLieu_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "CauHoi" DROP CONSTRAINT IF EXISTS "FK_CauHoi_MaNguoiDung_NguoiDung";
ALTER TABLE "CauHoi" ADD CONSTRAINT "FK_CauHoi_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "CauHoi" DROP CONSTRAINT IF EXISTS "FK_CauHoi_MaMonHoc_MonHoc";
ALTER TABLE "CauHoi" ADD CONSTRAINT "FK_CauHoi_MaMonHoc_MonHoc" FOREIGN KEY ("MaMonHoc") REFERENCES "MonHoc"("MaMonHoc");
ALTER TABLE "CauHoi" DROP CONSTRAINT IF EXISTS "FK_CauHoi_MaCongDong_CongDong";
ALTER TABLE "CauHoi" ADD CONSTRAINT "FK_CauHoi_MaCongDong_CongDong" FOREIGN KEY ("MaCongDong") REFERENCES "CongDong"("MaCongDong");
ALTER TABLE "CauTraLoi" DROP CONSTRAINT IF EXISTS "FK_CauTraLoi_MaCauHoi_CauHoi";
ALTER TABLE "CauTraLoi" ADD CONSTRAINT "FK_CauTraLoi_MaCauHoi_CauHoi" FOREIGN KEY ("MaCauHoi") REFERENCES "CauHoi"("MaCauHoi");
ALTER TABLE "CauTraLoi" DROP CONSTRAINT IF EXISTS "FK_CauTraLoi_MaNguoiDung_NguoiDung";
ALTER TABLE "CauTraLoi" ADD CONSTRAINT "FK_CauTraLoi_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "BinhChonCauTraLoi" DROP CONSTRAINT IF EXISTS "FK_BinhChonCauTraLoi_MaCauTraLoi_CauTraLoi";
ALTER TABLE "BinhChonCauTraLoi" ADD CONSTRAINT "FK_BinhChonCauTraLoi_MaCauTraLoi_CauTraLoi" FOREIGN KEY ("MaCauTraLoi") REFERENCES "CauTraLoi"("MaCauTraLoi");
ALTER TABLE "BinhChonCauTraLoi" DROP CONSTRAINT IF EXISTS "FK_BinhChonCauTraLoi_MaNguoiDung_NguoiDung";
ALTER TABLE "BinhChonCauTraLoi" ADD CONSTRAINT "FK_BinhChonCauTraLoi_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "NhomHoc" DROP CONSTRAINT IF EXISTS "FK_NhomHoc_MaMonHoc_MonHoc";
ALTER TABLE "NhomHoc" ADD CONSTRAINT "FK_NhomHoc_MaMonHoc_MonHoc" FOREIGN KEY ("MaMonHoc") REFERENCES "MonHoc"("MaMonHoc");
ALTER TABLE "NhomHoc" DROP CONSTRAINT IF EXISTS "FK_NhomHoc_MaCongDong_CongDong";
ALTER TABLE "NhomHoc" ADD CONSTRAINT "FK_NhomHoc_MaCongDong_CongDong" FOREIGN KEY ("MaCongDong") REFERENCES "CongDong"("MaCongDong");
ALTER TABLE "NhomHoc" DROP CONSTRAINT IF EXISTS "FK_NhomHoc_MaTruongNhom_NguoiDung";
ALTER TABLE "NhomHoc" ADD CONSTRAINT "FK_NhomHoc_MaTruongNhom_NguoiDung" FOREIGN KEY ("MaTruongNhom") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "ThanhVienNhom" DROP CONSTRAINT IF EXISTS "FK_ThanhVienNhom_MaNhomHoc_NhomHoc";
ALTER TABLE "ThanhVienNhom" ADD CONSTRAINT "FK_ThanhVienNhom_MaNhomHoc_NhomHoc" FOREIGN KEY ("MaNhomHoc") REFERENCES "NhomHoc"("MaNhomHoc");
ALTER TABLE "ThanhVienNhom" DROP CONSTRAINT IF EXISTS "FK_ThanhVienNhom_MaNguoiDung_NguoiDung";
ALTER TABLE "ThanhVienNhom" ADD CONSTRAINT "FK_ThanhVienNhom_MaNguoiDung_NguoiDung" FOREIGN KEY ("MaNguoiDung") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "TinTruong" DROP CONSTRAINT IF EXISTS "FK_TinTruong_MaQuanTriVien_NguoiDung";
ALTER TABLE "TinTruong" ADD CONSTRAINT "FK_TinTruong_MaQuanTriVien_NguoiDung" FOREIGN KEY ("MaQuanTriVien") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "TinTruong" DROP CONSTRAINT IF EXISTS "FK_TinTruong_MaCongDong_CongDong";
ALTER TABLE "TinTruong" ADD CONSTRAINT "FK_TinTruong_MaCongDong_CongDong" FOREIGN KEY ("MaCongDong") REFERENCES "CongDong"("MaCongDong");
ALTER TABLE "ThongBao" DROP CONSTRAINT IF EXISTS "FK_ThongBao_MaNguoiNhan_NguoiDung";
ALTER TABLE "ThongBao" ADD CONSTRAINT "FK_ThongBao_MaNguoiNhan_NguoiDung" FOREIGN KEY ("MaNguoiNhan") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "ThongBao" DROP CONSTRAINT IF EXISTS "FK_ThongBao_MaNguoiThucHien_NguoiDung";
ALTER TABLE "ThongBao" ADD CONSTRAINT "FK_ThongBao_MaNguoiThucHien_NguoiDung" FOREIGN KEY ("MaNguoiThucHien") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "BaoCaoViPham" DROP CONSTRAINT IF EXISTS "FK_BaoCaoViPham_MaNguoiBaoCao_NguoiDung";
ALTER TABLE "BaoCaoViPham" ADD CONSTRAINT "FK_BaoCaoViPham_MaNguoiBaoCao_NguoiDung" FOREIGN KEY ("MaNguoiBaoCao") REFERENCES "NguoiDung"("MaNguoiDung");
ALTER TABLE "BaoCaoViPham" DROP CONSTRAINT IF EXISTS "FK_BaoCaoViPham_MaAdminXuLy_NguoiDung";
ALTER TABLE "BaoCaoViPham" ADD CONSTRAINT "FK_BaoCaoViPham_MaAdminXuLy_NguoiDung" FOREIGN KEY ("MaAdminXuLy") REFERENCES "NguoiDung"("MaNguoiDung");

-- =========================================================================
-- PHẦN 3: RÀNG BUỘC DUY NHẤT (UNIQUE) & KIỂM TRA (CHECK)
-- =========================================================================
CREATE UNIQUE INDEX IF NOT EXISTS "UQ_NguoiDung_MaSinhVien" ON "NguoiDung"("MaSinhVien") WHERE "MaSinhVien" IS NOT NULL;
ALTER TABLE "NguoiDung" DROP CONSTRAINT IF EXISTS "UQ_NguoiDung_Email";
ALTER TABLE "NguoiDung" ADD CONSTRAINT "UQ_NguoiDung_Email" UNIQUE ("Email");
ALTER TABLE "KetBan" DROP CONSTRAINT IF EXISTS "UQ_KetBan_Gui_Nhan";
ALTER TABLE "KetBan" ADD CONSTRAINT "UQ_KetBan_Gui_Nhan" UNIQUE ("MaNguoiGui", "MaNguoiNhan");
ALTER TABLE "KetBan" DROP CONSTRAINT IF EXISTS "CK_KetBan_KhacNguoi";
ALTER TABLE "KetBan" ADD CONSTRAINT "CK_KetBan_KhacNguoi" CHECK ("MaNguoiGui" <> "MaNguoiNhan");
ALTER TABLE "TuongTac" DROP CONSTRAINT IF EXISTS "UQ_TuongTac_BaiViet_NguoiDung";
ALTER TABLE "TuongTac" ADD CONSTRAINT "UQ_TuongTac_BaiViet_NguoiDung" UNIQUE ("MaBaiViet", "MaNguoiDung");
ALTER TABLE "MonHoc" DROP CONSTRAINT IF EXISTS "UQ_MonHoc_KyHieuMonHoc";
ALTER TABLE "MonHoc" ADD CONSTRAINT "UQ_MonHoc_KyHieuMonHoc" UNIQUE ("KyHieuMonHoc");
ALTER TABLE "TaiLieu" DROP CONSTRAINT IF EXISTS "UQ_TaiLieu_DuongDanTep";
ALTER TABLE "TaiLieu" ADD CONSTRAINT "UQ_TaiLieu_DuongDanTep" UNIQUE ("DuongDanTep");
ALTER TABLE "BinhChonCauTraLoi" DROP CONSTRAINT IF EXISTS "UQ_BinhChon_CauTraLoi_NguoiDung";
ALTER TABLE "BinhChonCauTraLoi" ADD CONSTRAINT "UQ_BinhChon_CauTraLoi_NguoiDung" UNIQUE ("MaCauTraLoi", "MaNguoiDung");
ALTER TABLE "CongDong" DROP CONSTRAINT IF EXISTS "CK_CongDong_CapDo";
ALTER TABLE "CongDong" ADD CONSTRAINT "CK_CongDong_CapDo" CHECK ("CapDo" IN ('Truong', 'Khoa', 'Nganh', 'KhoaHoc', 'Lop'));
ALTER TABLE "NguoiDung" DROP CONSTRAINT IF EXISTS "CK_NguoiDung_VaiTro";
ALTER TABLE "NguoiDung" ADD CONSTRAINT "CK_NguoiDung_VaiTro" CHECK ("VaiTro" IN ('SinhVien', 'QuanTriVien'));
ALTER TABLE "DanhGiaTaiLieu" DROP CONSTRAINT IF EXISTS "CK_DanhGiaTaiLieu_Diem";
ALTER TABLE "DanhGiaTaiLieu" ADD CONSTRAINT "CK_DanhGiaTaiLieu_Diem" CHECK ("Diem" BETWEEN 1 AND 5);
ALTER TABLE "NhomHoc" DROP CONSTRAINT IF EXISTS "CK_NhomHoc_SiSo";
ALTER TABLE "NhomHoc" ADD CONSTRAINT "CK_NhomHoc_SiSo" CHECK ("SoThanhVienToiDa" >= 2 AND "SoThanhVienHienTai" <= "SoThanhVienToiDa");
ALTER TABLE "TinNhan" DROP CONSTRAINT IF EXISTS "CK_TinNhan_Dich";
ALTER TABLE "TinNhan" ADD CONSTRAINT "CK_TinNhan_Dich" CHECK (("MaNguoiNhan" IS NOT NULL AND "MaNhomHoc" IS NULL) OR ("MaNguoiNhan" IS NULL AND "MaNhomHoc" IS NOT NULL));

-- =========================================================================
-- PHẦN 4: CHỈ MỤC TỐI ƯU TRUY VẤN (INDEXES)
-- =========================================================================
CREATE INDEX IF NOT EXISTS "IX_CongDong_Cha_CapDo" ON "CongDong"("MaCongDongCha", "CapDo");
CREATE INDEX IF NOT EXISTS "IX_BaiViet_CongDong_NgayTao" ON "BaiViet"("MaCongDong", "NgayTao" DESC);
CREATE INDEX IF NOT EXISTS "IX_TaiLieu_MonHoc_CongDong" ON "TaiLieu"("MaMonHoc", "MaCongDong");
CREATE INDEX IF NOT EXISTS "IX_CauHoi_MonHoc_NgayTao" ON "CauHoi"("MaMonHoc", "NgayTao" DESC);
CREATE INDEX IF NOT EXISTS "IX_ThongBao_NguoiNhan_DaDoc" ON "ThongBao"("MaNguoiNhan", "DaDoc", "NgayTao" DESC);
CREATE INDEX IF NOT EXISTS "IX_TinNhan_Dich_ThoiGian" ON "TinNhan"("MaNguoiNhan", "MaNhomHoc", "ThoiGianGui" DESC);
```

### 4.3. Script dữ liệu mẫu khởi tạo (`database/02_seed_5_cap_truong.sql`)

```sql
-- =========================================================================
-- DỮ LIỆU MẪU KHỞI TẠO (SEED DATA) - POSTGRESQL 18 BẢNG
-- Tạo cây Cộng đồng 5 cấp tự tham chiếu (Trường -> Khoa -> Ngành -> Khóa -> Lớp) & Môn học
-- =========================================================================

DO $$
DECLARE
    v_truong  BIGINT;
    v_khoa    BIGINT;
    v_nganh   BIGINT;
    v_khoahoc BIGINT;
    v_lop     BIGINT;
BEGIN
    SELECT "MaCongDong" INTO v_truong FROM "CongDong" WHERE "KyHieu" = 'CNTT-DEMO' AND "CapDo" = 'Truong';
    IF v_truong IS NULL THEN
        INSERT INTO "CongDong" ("MaCongDongCha", "KyHieu", "TenCongDong", "CapDo")
        VALUES (NULL, 'CNTT-DEMO', 'Đại học Công Nghệ Thông Tin (Demo)', 'Truong')
        RETURNING "MaCongDong" INTO v_truong;
    END IF;

    SELECT "MaCongDong" INTO v_khoa FROM "CongDong" WHERE "MaCongDongCha" = v_truong AND "KyHieu" = 'CNTT';
    IF v_khoa IS NULL THEN
        INSERT INTO "CongDong" ("MaCongDongCha", "KyHieu", "TenCongDong", "CapDo")
        VALUES (v_truong, 'CNTT', 'Khoa Công nghệ Thông tin', 'Khoa')
        RETURNING "MaCongDong" INTO v_khoa;
    END IF;

    SELECT "MaCongDong" INTO v_nganh FROM "CongDong" WHERE "MaCongDongCha" = v_khoa AND "KyHieu" = 'MMT';
    IF v_nganh IS NULL THEN
        INSERT INTO "CongDong" ("MaCongDongCha", "KyHieu", "TenCongDong", "CapDo")
        VALUES (v_khoa, 'MMT', 'Mạng máy tính & Truyền thông', 'Nganh')
        RETURNING "MaCongDong" INTO v_nganh;
    END IF;

    SELECT "MaCongDong" INTO v_khoahoc FROM "CongDong" WHERE "MaCongDongCha" = v_nganh AND "KyHieu" = 'K2022';
    IF v_khoahoc IS NULL THEN
        INSERT INTO "CongDong" ("MaCongDongCha", "KyHieu", "TenCongDong", "CapDo", "NamBatDau")
        VALUES (v_nganh, 'K2022', 'Khóa 2022', 'KhoaHoc', 2022)
        RETURNING "MaCongDong" INTO v_khoahoc;
    END IF;

    SELECT "MaCongDong" INTO v_lop FROM "CongDong" WHERE "MaCongDongCha" = v_khoahoc AND "KyHieu" = 'D22CQCN01';
    IF v_lop IS NULL THEN
        INSERT INTO "CongDong" ("MaCongDongCha", "KyHieu", "TenCongDong", "CapDo")
        VALUES (v_khoahoc, 'D22CQCN01', 'Lớp D22CQCN01', 'Lop')
        RETURNING "MaCongDong" INTO v_lop;
    END IF;

    INSERT INTO "MonHoc" ("MaTruong", "KyHieuMonHoc", "TenMonHoc", "SoTinChi")
    VALUES
      (v_truong, 'LTM01', 'Lập trình mạng', 3),
      (v_truong, 'CSDL01', 'Cơ sở dữ liệu', 3),
      (v_truong, 'CTDL01', 'Cấu trúc dữ liệu & Giải thuật', 3)
    ON CONFLICT ("KyHieuMonHoc") DO NOTHING;
END $$;
```

---

## 5. ĐẶC TẢ CHI TIẾT 10 MODULE (CSDL · API/WS · TKINTER VIEWS · VẤN ĐÁP)

#### M1: Tài khoản, Hồ sơ & Quên mật khẩu (OTP) — Phụ trách: **Nguyễn Ngô Tú Anh** (*Leader*)
- **Thư mục MVC GitHub:** `src/Modules/M01_Auth_TaiKhoan__TuAnh/`
- **Chức năng:** Đăng ký theo lớp (cấp MaLop trỏ cây CongDong), Đăng nhập JWT (theo VaiTro trong NguoiDung), Đăng xuất, Đổi mật khẩu, Quên MK qua MaOTP/HanOTP, Cập nhật hồ sơ & Đổi lớp.
- **Bảng PostgreSQL:** `"NguoiDung"`
- **API / WebSocket:** `POST /api/m01/auth/register`, `POST /api/m01/auth/login`, `POST /api/m01/auth/logout`, `PUT /api/m01/users/password`, `POST /api/m01/auth/forgot-otp`, `POST /api/m01/auth/reset-pw`, `PUT /api/m01/users/profile`
- **Desktop Views (Tkinter):** `Views/m01_view.py (Tkinter: Đăng ký, Đăng nhập, Quên MK OTP, Hồ sơ & Đổi lớp)`
- **Quy trình 4 Bước:**
  - **B1 — Base Python MVC & DB:** Dựng FastAPI, Tkinter Client & kết nối PostgreSQL psycopg vào bảng NguoiDung.
  - **B2 — Controller & Middleware:** Code m01_controller.py & auth_middleware.py xác thực JWT và kiểm tra TrangThai trong NguoiDung.
  - **B3 — Tkinter Desktop View:** Dựng Frame Đăng ký (chọn Trường→Lớp từ M02), Đăng nhập, Quên MK OTP & Hồ sơ.
  - **B4 — Demo & KPI:** Test trọn luồng từ Tkinter Client: Đăng ký → Đăng nhập → Quên MK OTP → Đổi MK / Cập nhật hồ sơ.
- **KPI hoàn thành:** Deploy Render ổn định, Tkinter Client đăng ký/đăng nhập/đổi lớp mượt mà trên bảng NguoiDung.
- **Kiến thức & Câu hỏi vấn đáp:** Cách xác thực JWT qua Header Bearer và WebSocket; luồng người dùng khôi phục mật khẩu bằng MaOTP & cập nhật MaLop khi đổi lớp.
  - 1) Khi sinh viên chọn Lớp lúc đăng ký, bảng NguoiDung lưu thông tin gì để biết bạn thuộc Khoa và Trường nào?
  - 2) Luồng Quên mật khẩu xử lý mã OTP và hạn dùng trên bảng NguoiDung ra sao?

#### M2: Cây Cộng đồng 5 Cấp (Trường → Lớp) — Phụ trách: **Duy** (*Full-stack Module*)
- **Thư mục MVC GitHub:** `src/Modules/M02_CongDong_5Cap__Duy/`
- **Chức năng:** Quản lý trọn vẹn 5 cấp (Truong → Khoa → Nganh → KhoaHoc → Lop) trên 1 bảng CongDong tự tham chiếu MaCongDongCha; cấp API lọc nối tiếp cho màn Đăng ký & Hồ sơ; trang Admin sửa/ngừng đơn vị.
- **Bảng PostgreSQL:** `"CongDong"`
- **API / WebSocket:** `GET /api/m02/communities/roots`, `GET /api/m02/communities/{parentId}/children`, `GET /api/m02/communities/chain/{lopId}`, `CRUD /api/m02/admin/communities`
- **Desktop Views (Tkinter):** `Views/m02_view.py (Tkinter: Combobox nối tiếp 5 cấp, Cây Cộng đồng, Admin 5 cấp)`
- **Quy trình 4 Bước:**
  - **B1 — Model & Seed 5 cấp:** Tạo Model truy vấn đệ quy/nối tiếp bảng CongDong & script 02_seed_5_cap_truong.sql.
  - **B2 — Controller 5 cấp:** Viết API lấy danh sách con theo MaCongDongCha và suy ngược đủ 5 cấp từ MaLop của sinh viên.
  - **B3 — Tkinter Desktop View:** Dựng Combobox cascading Trường→Khoa→Ngành→Khóa→Lớp và khung Admin thêm/sửa đơn vị.
  - **B4 — Demo & KPI:** Test chọn lớp ở Đăng ký & thêm mới 1 lớp ở màn Admin hiện ngay sang danh sách chọn.
- **KPI hoàn thành:** Biểu diễn đủ 5 cấp đào tạo chỉ bằng 1 bảng CongDong duy nhất, gọn nhẹ không dư bảng.
- **Kiến thức & Câu hỏi vấn đáp:** Cấu trúc cây tự tham chiếu (Self-referencing FK MaCongDongCha) giúp vừa quản lý Trường/Khoa/Ngành/Khóa/Lớp vừa làm phạm vi bài viết/tài liệu.
  - 1) Tại sao chỉ cần 1 bảng CongDong có cột MaCongDongCha lại quản lý được cả 5 cấp Trường–Khoa–Ngành–Khóa–Lớp?
  - 2) Khi sinh viên chuyển từ Lớp A sang Lớp B, làm sao hệ thống biết đủ 5 cộng đồng mới của bạn ấy?

#### M3: Bài viết, Tương tác & Kết bạn — Phụ trách: **Duy** (*Full-stack Module*)
- **Thư mục MVC GitHub:** `src/Modules/M03_BaiViet_KetBan__Duy/`
- **Chức năng:** Đăng/Sửa/Xóa bài viết theo phạm vi CongDong (kèm đường dẫn TepDinhKem tùy chọn); Bình luận, Thích (chống trùng 1 lượt/người/bài); Tìm bạn học & Kết bạn 2 chiều (KetBan).
- **Bảng PostgreSQL:** `"BaiViet"`, `"BinhLuan"`, `"TuongTac"`, `"KetBan"`
- **API / WebSocket:** `CRUD /api/m03/posts`, `POST /api/m03/posts/{id}/comments`, `POST /api/m03/posts/{id}/like`, `POST /api/m03/friends/request`, `PUT /api/m03/friends/{id}/respond`
- **Desktop Views (Tkinter):** `Views/m03_view.py (Tkinter: Đăng/Sửa bài, Bình luận, Thích, Tìm & Kết bạn)`
- **Quy trình 4 Bước:**
  - **B1 — Model 4 bảng MXH:** Viết Model PostgreSQL cho BaiViet, BinhLuan, TuongTac (UNIQUE bài+người) và KetBan.
  - **B2 — Controller:** Code API kiểm tra đúng tác giả khi sửa/xóa bài, chống thích trùng, gửi thông báo khi có bình luận/kết bạn.
  - **B3 — Tkinter Desktop View:** Dựng khung soạn/sửa bài viết, danh sách bình luận, nút Thích tức thì và tab Kết bạn.
  - **B4 — Demo & KPI:** Test trọn luồng từ Tkinter: Đăng bài → Sửa/Xóa → Thích/Bình luận → Tìm & Chấp nhận kết bạn.
- **KPI hoàn thành:** Chỉ tác giả sửa/xóa được bài viết của mình, không trùng lượt thích hay lời mời kết bạn.
- **Kiến thức & Câu hỏi vấn đáp:** Cách kiểm tra quyền sở hữu bài viết trên Server và thiết kế quan hệ bạn bè 2 chiều trong KetBan.
  - 1) Khi bạn nhấn nút Thích bài viết rồi bấm lần nữa, hệ thống xử lý thế nào ở bảng TuongTac?
  - 2) Làm thế nào đảm bảo người khác không thể sửa hoặc xóa bài viết của bạn?

#### M4: Tài liệu Học tập & Truyền tệp — Phụ trách: **Huy** (*Full-stack Module*)
- **Thư mục MVC GitHub:** `src/Modules/M04_TaiLieu_TepTin__Huy/`
- **Chức năng:** Danh mục MonHoc; Tải lên tài liệu (<20MB PDF/DOCX/ảnh) lưu thông tin thẳng vào bảng TaiLieu; Tải tệp về máy và cộng SoLuotTai; Tìm kiếm theo môn & Chấm điểm 1–5★ (DanhGiaTaiLieu).
- **Bảng PostgreSQL:** `"MonHoc"`, `"TaiLieu"`, `"DanhGiaTaiLieu"`
- **API / WebSocket:** `GET /api/m04/subjects`, `POST /api/m04/documents/upload`, `GET /api/m04/documents/search`, `GET /api/m04/documents/{id}/download`, `POST /api/m04/documents/{id}/rate`
- **Desktop Views (Tkinter):** `Views/m04_view.py (Tkinter: Kho tài liệu, Upload + Progressbar, Tải về & Chấm 1–5★)`
- **Quy trình 4 Bước:**
  - **B1 — Model 3 bảng Tài liệu:** Tạo Model cho MonHoc, TaiLieu (lưu kèm TenTep, DuongDanTep, SoLuotTai) và DanhGiaTaiLieu (1–5★).
  - **B2 — Controller Upload/Download:** Viết API nhận file multipart (<20MB), tải về FileResponse cộng SoLuotTai và tính lại DiemDanhGiaTB.
  - **B3 — Tkinter Desktop View:** Dựng màn hình tìm tài liệu theo môn, filedialog chọn file + thanh tiến trình và chấm 1–5 sao.
  - **B4 — Demo & KPI:** Test từ chối tệp vượt quá 20MB/sai loại, tải lên PDF thành công, tải về máy & chấm 5★.
- **KPI hoàn thành:** Truyền nhận tệp nguyên vẹn, kiểm tra định dạng/dung lượng an toàn, cập nhật điểm TB chuẩn xác.
- **Kiến thức & Câu hỏi vấn đáp:** Cách truyền file nhị phân giữa Tkinter Client và FastAPI Server, kiểm tra loại tệp an toàn ở phía Server và tính điểm trung bình sao.
  - 1) Khi sinh viên tải tài liệu về máy, những thông tin nào trên bảng TaiLieu được cập nhật?
  - 2) Nếu 1 sinh viên đánh giá lại số sao cho tài liệu đã chấm trước đó thì hệ thống xử lý sao?

#### M5: Hỏi đáp Học thuật (Q&A & Upvote) — Phụ trách: **Huy** (*Full-stack Module*)
- **Thư mục MVC GitHub:** `src/Modules/M05_HoiDap_QA__Huy/`
- **Chức năng:** Đặt câu hỏi theo MonHoc kèm từ khóa TheTuKhoa (#Socket, #SQL, #Python); Gửi câu trả lời; Bấm Upvote hữu ích (1 lần/người qua BinhChonCauTraLoi); Chủ câu hỏi chốt Đáp án đúng.
- **Bảng PostgreSQL:** `"CauHoi"`, `"CauTraLoi"`, `"BinhChonCauTraLoi"`
- **API / WebSocket:** `CRUD /api/m05/questions`, `POST /api/m05/questions/{id}/answers`, `POST /api/m05/answers/{id}/upvote`, `PUT /api/m05/answers/{id}/correct`
- **Desktop Views (Tkinter):** `Views/m05_view.py (Tkinter: Diễn đàn Q&A, Lọc môn/thẻ, Upvote & Chốt đáp án đúng)`
- **Quy trình 4 Bước:**
  - **B1 — Model 3 bảng Q&A:** Tạo Model cho CauHoi (có cột TheTuKhoa, DaGiaiQuyet), CauTraLoi và BinhChonCauTraLoi.
  - **B2 — Controller Q&A:** Viết API tạo câu hỏi, trả lời (gọi thông báo cho tác giả), toggle Upvote và chốt Đáp án đúng.
  - **B3 — Tkinter Desktop View:** Dựng danh sách câu hỏi, ô lọc theo Môn/#Thẻ, nút Upvote & nút Chốt đáp án cho tác giả.
  - **B4 — Demo & KPI:** Test trọn luồng đặt câu hỏi → bạn trả lời → cộng đồng Upvote → tác giả chốt đáp án đúng.
- **KPI hoàn thành:** Không vote trùng trên 1 câu trả lời, đáp án đúng được ghim nổi bật lên đầu danh sách.
- **Kiến thức & Câu hỏi vấn đáp:** Cách dùng UNIQUE(MaCauTraLoi, MaNguoiDung) trong BinhChonCauTraLoi để chống bình chọn trùng lặp và kiểm tra quyền chủ câu hỏi.
  - 1) Làm thế nào để mỗi sinh viên chỉ upvote tối đa 1 lần cho một câu trả lời?
  - 2) Ai có quyền bấm đánh dấu 'Đáp án đúng' cho một câu hỏi?

#### M6: Nhóm học Tập (Study Groups) — Phụ trách: **Bảo** (*Full-stack Module*)
- **Thư mục MVC GitHub:** `src/Modules/M06_NhomHoc__Bao/`
- **Chức năng:** Sinh viên tạo nhóm học (thành Trưởng nhóm); Tìm & Gửi đơn xin gia nhập (lưu ngay vào ThanhVienNhom trạng thái 'ChoDuyet'); Trưởng nhóm duyệt/từ chối theo sĩ số tối đa; Đổi sức chứa & Bàn giao trưởng nhóm khi rời.
- **Bảng PostgreSQL:** `"NhomHoc"`, `"ThanhVienNhom"`
- **API / WebSocket:** `POST /api/m06/groups`, `GET /api/m06/groups/search`, `POST /api/m06/groups/{id}/join`, `PUT /api/m06/groups/{id}/requests/{uid}`, `PUT /api/m06/groups/{id}/capacity`, `POST /api/m06/groups/{id}/transfer-leave`
- **Desktop Views (Tkinter):** `Views/m06_view.py (Tkinter: Tìm nhóm, Xin vào nhóm, Bảng duyệt đơn Trưởng nhóm & Rời nhóm)`
- **Quy trình 4 Bước:**
  - **B1 — Model 2 bảng Nhóm:** Tạo Model cho NhomHoc và ThanhVienNhom (dùng TrangThai ChoDuyet/DaThamGia/TuChoi thay vì tách nhiều bảng).
  - **B2 — Controller & Sĩ số:** Viết API tạo nhóm, gửi đơn, duyệt đơn (kiểm tra SoThanhVienHienTai < SoThanhVienToiDa) và chuyển trưởng nhóm.
  - **B3 — Tkinter Desktop View:** Dựng danh sách nhóm học, khung duyệt đơn của Trưởng nhóm & hộp chọn người kế nhiệm khi rời nhóm.
  - **B4 — Demo & KPI:** Test xin vào nhóm → Trưởng nhóm duyệt sát sĩ số → Trưởng nhóm chuyển quyền rồi rời nhóm.
- **KPI hoàn thành:** Không bao giờ vượt sĩ số tối đa hay để nhóm vô chủ khi Trưởng nhóm rời đi.
- **Kiến thức & Câu hỏi vấn đáp:** Cách gộp đơn chờ duyệt và thành viên vào chung 1 bảng ThanhVienNhom qua cột TrangThai và quy tắc chuyển MaTruongNhom.
  - 1) Khi nhóm học đã đủ SoThanhVienToiDa thì Trưởng nhóm thao tác thế nào nếu muốn nhận thêm bạn mới?
  - 2) Nếu Trưởng nhóm bấm rời nhóm khi vẫn còn thành viên khác thì giao diện yêu cầu làm gì trước?

#### M7: Campus (Tin tức, Học bổng, Sự kiện) — Phụ trách: **Bảo** (*Full-stack Module*)
- **Thư mục MVC GitHub:** `src/Modules/M07_Campus__Bao/`
- **Chức năng:** Sinh viên xem & lọc tin nhà trường (SuKien, HocBong, ThucTap, CLB, ThongBao) theo CongDong; Admin đăng mới, chỉnh sửa, ẩn/xóa tin Campus và phát thông báo tới sinh viên.
- **Bảng PostgreSQL:** `"TinTruong"`
- **API / WebSocket:** `GET /api/m07/campus`, `POST /api/m07/admin/campus`, `PUT /api/m07/admin/campus/{id}`, `DELETE /api/m07/admin/campus/{id}`
- **Desktop Views (Tkinter):** `Views/m07_view.py (Tkinter: Tab Campus Sinh viên & Frame Quản trị Campus)`
- **Quy trình 4 Bước:**
  - **B1 — Model TinTruong:** Viết Model truy vấn TinTruong (lọc TrangThai = 'CongBo', phân trang LIMIT/OFFSET).
  - **B2 — Controller & Phân quyền:** Viết API cho sinh viên lọc tin và API cho Admin đăng/sửa/ẩn tin kèm đẩy thông báo M09.
  - **B3 — Tkinter Desktop View:** Dựng tab Campus cho Sinh viên và Frame đăng tin gắn vào màn hình Admin M10.
  - **B4 — Demo & KPI:** Test Admin đăng tin Sự kiện/Học bổng mới → Sinh viên mở tab Campus thấy ngay lập tức.
- **KPI hoàn thành:** Tin mới hiển thị đúng chuyên mục và phạm vi Trường/Khoa, chỉ Admin được quyền đăng/sửa.
- **Kiến thức & Câu hỏi vấn đáp:** Phân trang kết quả bằng LIMIT/OFFSET và kiểm tra vai trò QuanTriVien khi Admin thao tác đăng/ẩn tin.
  - 1) Sinh viên tự tìm cách gọi đường dẫn đăng tin Campus của Admin thì bị chặn ở đâu?
  - 2) Vì sao danh sách tin Campus nên hỗ trợ phân trang thay vì tải toàn bộ cùng lúc?

#### M8: Khung Tkinter Chung, Bảng tin & Riêng tư — Phụ trách: **Thái** (*UI Lead*)
- **Thư mục MVC GitHub:** `src/Modules/M08_BangTin_RiengTu__Thai/`
- **Chức năng:** Dựng khung cửa sổ Tkinter chính (Sidebar, Header, chuyển đổi 10 Module trong client_app.py) cho cả nhóm; Bảng tin thông minh lọc theo 5 cấp cộng đồng & 4 chủ đề; Quyền riêng tư (CaiDatRiengTu trong NguoiDung) & Chặn người dùng (KetBan DaChan).
- **Bảng PostgreSQL:** `"NguoiDung"`, `"KetBan"`
- **API / WebSocket:** `GET /api/m08/feed`, `PUT /api/m08/privacy`, `POST /api/m08/block/{targetId}`, `DELETE /api/m08/block/{targetId}`
- **Desktop Views (Tkinter):** `client_app.py (Khung Tkinter chung cả nhóm)`, `Views/m08_view.py (Bảng tin 5 cấp & Cài đặt Riêng tư/Chặn)`
- **Quy trình 4 Bước:**
  - **B1 — Model Feed & Riêng tư:** Viết truy vấn hợp nhất Bảng tin từ BaiViet/TaiLieu/CauHoi/TinTruong và đọc/lưu CaiDatRiengTu, trạng thái DaChan.
  - **B2 — Controller & Lọc quyền:** Viết Controller GET /api/m08/feed ưu tiên nội dung từ Lớp → Trường, đồng thời ẩn bài của người đang bị chặn.
  - **B3 — Tkinter Layout & Views:** Dựng khung client_app.py để các thành viên nhúng View vào, cùng màn hình Bảng tin & Cài đặt riêng tư.
  - **B4 — Demo & KPI:** Test ẩn SĐT/Email và chặn 1 tài khoản → người bị chặn không thấy thông tin riêng tư và không nhắn tin được.
- **KPI hoàn thành:** Khung App Desktop thống nhất cho 5 thành viên, Bảng tin tải nhanh và tôn trọng đúng quyền riêng tư.
- **Kiến thức & Câu hỏi vấn đáp:** Lý do lọc ẩn dữ liệu nhạy cảm (SĐT/Email) và người bị chặn ngay ở Server trước khi trả về Client.
  - 1) Khi bạn A bật ẩn Số điện thoại trong cài đặt riêng tư, dữ liệu nên được che giấu tại Server hay tại máy người xem?
  - 2) Bảng tin ưu tiên nội dung theo thứ tự cộng đồng nào?

#### M9: Nhắn tin Realtime & Thông báo — Phụ trách: **Thái** (*UI Lead*)
- **Thư mục MVC GitHub:** `src/Modules/M09_Chat_ThongBao_Realtime__Thai/`
- **Chức năng:** Mở kênh WebSocket /ws cho phép nhắn tin 1-1 và chat nhóm trực tiếp (lưu lịch sử TinNhan); Chuông thông báo & hộp thư ThongBao; cung cấp hàm send_notification() cho Duy, Huy, Bảo đẩy thông báo tức thì.
- **Bảng PostgreSQL:** `"TinNhan"`, `"ThongBao"`
- **API / WebSocket:** `GET /api/m09/chat/history`, `POST /api/m09/chat/send`, `GET /api/m09/notifications`, `PUT /api/m09/notifications/{id}/read`, `WS /ws (chat_message, notification)`
- **Desktop Views (Tkinter):** `Views/m09_view.py (Tkinter: Khung Chat 1-1 & Nhóm, Chuông thông báo & Popup)`
- **Quy trình 4 Bước:**
  - **B1 — Model TinNhan & ThongBao:** Tạo Model cho TinNhan (chat 1-1 & chat nhóm) và ThongBao; chốt hàm send_notification() dùng chung.
  - **B2 — WebSocket Server /ws:** Quản lý danh sách user đang kết nối WebSocket, kiểm tra chặn trước khi gửi tin và lưu DB khi user offline.
  - **B3 — Tkinter Chat & Chuông TB:** Dựng khung chat hai chiều và chuông thông báo hiển thị tin mới ngay lập tức trên App Desktop.
  - **B4 — Demo & KPI:** Mở 2 cửa sổ App Desktop Tkinter nối chung Server Render test nhắn tin 1-1, chat nhóm và chuông thông báo.
- **KPI hoàn thành:** Tin nhắn và thông báo hiển thị tức thì khi hai máy cùng mở app, không mất tin khi đối phương offline.
- **Kiến thức & Câu hỏi vấn đáp:** Cơ chế WebSocket hai chiều giúp Server chủ động đẩy tin nhắn mới tới đúng người nhận mà Client không cần bấm tải lại.
  - 1) Khi bạn B đang tắt ứng dụng lúc bạn A nhắn tin, tin nhắn đó có bị mất không? Khi bạn B mở app lại thì xem ở đâu?
  - 2) WebSocket giúp ích gì cho tính năng Chat và Thông báo so với cách gửi HTTP thông thường?

#### M10: Quản trị Hệ thống & Kiểm duyệt (Admin) — Phụ trách: **Nguyễn Ngô Tú Anh** (*Leader*)
- **Thư mục MVC GitHub:** `src/Modules/M10_QuanTri_KiemDuyet__TuAnh/`
- **Chức năng:** Quản lý danh sách tài khoản (đổi vai trò, khóa/mở khóa chống khóa Admin cuối cùng); Kiểm duyệt đơn BaoCaoViPham (bác bỏ, ẩn, xóa mềm nội dung vi phạm hoặc khóa tài khoản, lưu thẳng kết quả xử lý trên BaoCaoViPham); nhúng View của M02 & M07.
- **Bảng PostgreSQL:** `"BaoCaoViPham"`, `"NguoiDung"`
- **API / WebSocket:** `GET /api/m10/admin/users`, `PUT /api/m10/admin/users/{id}/lock`, `PUT /api/m10/admin/users/{id}/role`, `GET /api/m10/admin/reports`, `PUT /api/m10/admin/reports/{id}`
- **Desktop Views (Tkinter):** `Views/m10_view.py (Tkinter Tab Admin: Quản lý Tài khoản & Kiểm duyệt Vi phạm)`
- **Quy trình 4 Bước:**
  - **B1 — Model Kiểm duyệt:** Tạo Model Python truy vấn BaoCaoViPham và cập nhật trạng thái/vai trò trên NguoiDung.
  - **B2 — Controller Admin:** Viết Controller khóa/đổi vai trò (ngăn khóa Admin cuối) và xử lý báo cáo vi phạm (ẩn/xóa nội dung & gửi thông báo).
  - **B3 — Tkinter Admin Dashboard:** Dựng tab Quản lý tài khoản, tab Duyệt báo cáo và ghép View Cây 5 cấp (M02) + Campus (M07) vào chung.
  - **B4 — Demo & KPI:** Test báo cáo 1 bài viết → Admin vào duyệt ẩn bài → bài biến mất ngay khỏi Bảng tin sinh viên.
- **KPI hoàn thành:** Không khóa nhầm Admin cuối cùng, xử lý báo cáo nhanh gọn và lưu rõ quyết định kiểm duyệt trên BaoCaoViPham.
- **Kiến thức & Câu hỏi vấn đáp:** Tại sao luôn kiểm tra vai trò Quản trị viên trên Server thay vì chỉ dựa vào giao diện, và cách lưu kết quả xử lý ngay trên BaoCaoViPham.
  - 1) Nếu Admin cố khóa tài khoản Quản trị viên duy nhất còn lại trong hệ thống thì điều gì xảy ra?
  - 2) Khi sinh viên báo cáo một bài viết xấu và Admin chọn Ẩn nội dung, người đăng bài nhận được phản hồi thế nào?


---

## 6. MA TRẬN ĐIỂM NỐI TÍCH HỢP CHÉO

| Tình huống tích hợp | Bên gọi (Caller) | Dùng từ (Provider) | Kết quả & Yêu cầu |
| :--- | :--- | :--- | :--- |
| Mọi thao tác cần đăng nhập & quyền Admin | Duy, Huy, Bảo, Thái | verify_token & require_admin (Tú Anh M01) | Kiểm tra tài khoản hợp lệ & không bị khóa trong NguoiDung trước khi xử lý. |
| Chọn Trường → Lớp khi Đăng ký & Đổi lớp | Tú Anh (M01) | Controller cây CongDong của Duy (M02) | Nạp combobox 5 cấp Trường → Khoa → Ngành → Khóa → Lớp từ bảng CongDong. |
| Đính kèm tệp vào Bài viết | Duy (M03) | Helper kiểm tra & lưu tệp của Huy (M04) | Kiểm tra dung lượng <20MB/định dạng an toàn rồi gắn đường dẫn vào BaiViet.TepDinhKem. |
| Bình luận, Kết bạn, Trả lời Q&A, Duyệt nhóm, Campus | Duy (M03), Huy (M05), Bảo (M06, M07), Tú Anh (M10) | send_notification() & WebSocket /ws của Thái (M09) | Lưu ThongBao và đẩy tức thì tới thiết bị người nhận đang mở app. |
| Kiểm tra chặn trước khi Chat / Xem hồ sơ | Duy (M03), Thái (M09) | CaiDatRiengTu (NguoiDung) & DaChan (KetBan) (M08) | Ẩn SĐT/Email theo tùy chọn và chặn gửi tin nhắn nếu đã chặn nhau. |
| Tổng hợp Bảng tin theo 5 cấp cộng đồng | Thái (M08) | BaiViet (Duy), TaiLieu & CauHoi (Huy), TinTruong (Bảo) | Gộp nội dung theo phạm vi cộng đồng Lớp → Trường của sinh viên. |
| Ghép màn hình quản trị Trường & Campus | Duy (M02), Bảo (M07) | Admin Dashboard Tkinter của Tú Anh (M10) | Hiển thị chung trong giao diện Admin và dùng chung kiểm tra quyền require_admin. |
| Gửi Báo cáo vi phạm lên Admin | Duy (M03), Huy (M04, M05) | Luồng BaoCaoViPham của Tú Anh (M10) | Lưu đơn chờ duyệt vào BaoCaoViPham để Admin xem và quyết định ẩn/xóa/bác bỏ. |

---

## 7. LỘ TRÌNH 4 GIAI ĐOẠN & QUY TẮC GIT FLOW

### GIAI ĐOẠN 1: Dựng GitHub Modular MVC Python & Nối Render *(18 Bảng PostgreSQL + Khung M01..M10)*
- Tú Anh: Tạo Repo GitHub, mời đủ 4 bạn Collaborators; tạo PostgreSQL Free trên Render & chạy 01_schema_18_tables_postgres.sql; nối Render Web Service.
- Duy: Chạy 02_seed_5_cap_truong.sql & đẩy khung M02, M03 qua nhánh feature/.
- Huy, Bảo, Thái: Đẩy khung Models/Views(Tkinter)/Controllers của M04..M09 qua Pull Request.
- **Đầu ra bắt buộc:** GitHub đủ 5 Contributors + 10 thư mục MVC + Render báo Server Python & 18 bảng PostgreSQL sẵn sàng.

### GIAI ĐOẠN 2: Hoàn thiện từng Module Server – Client *(10 Module × 4 Bước End-to-End)*
- Mỗi thành viên tự code trọn 2 module mình sở hữu: Model (PostgreSQL 18 bảng) → Controller (FastAPI) → View (Tkinter Desktop).
- **Đầu ra bắt buộc:** Cả 10 Module chạy thông từ giao diện Desktop Tkinter lên Render Server xuống 18 bảng CSDL.

### GIAI ĐOẠN 3: Tích hợp chéo 22 Luồng Tương tác & Test đa máy *(Ghép giao diện + WebSocket Chat/Thông báo)*
- Nhúng các Frame Tkinter vào khung client_app.py (Thái M8) và Admin Dashboard (Tú Anh M10).
- Nối thông báo & chat WebSocket (Thái M9); mở 2 App Desktop Tkinter nối chung Render để kiểm thử trọn vẹn 22 luồng tương tác.
- **Đầu ra bắt buộc:** 2 máy chạy App Desktop Tkinter tương tác mượt mà với nhau thông qua Render Server.

### GIAI ĐOẠN 4: Chạy thử toàn bộ & Tập dượt Vấn đáp Bảo vệ *(Nộp Link Server Render + Repo GitHub)*
- Mỗi thành viên demo 2 phút trên App Desktop và trả lời trôi chảy câu hỏi về luồng tương tác + bảng dữ liệu của module mình.
- Cập nhật link Render Server và link GitHub vào báo cáo nộp giảng viên.
- **Đầu ra bắt buộc:** 100% thành viên nắm chắc cách tác nhân tương tác và cấu trúc 18 bảng tinh gọn.


### Quy tắc làm việc nhóm & Git Flow
- Tuyệt đối **không push trực tiếp lên nhánh `main`**; mỗi thành viên rẽ nhánh riêng theo module (`feature/m02-congdong`, `feature/m04-tailieu`...), code trong đúng thư mục `src/Modules/M0x_...` của mình và tạo **Pull Request** để Leader **Nguyễn Ngô Tú Anh** duyệt.
- Đảm bảo **cả 5 tài khoản GitHub** đều đã Accept lời mời **Collaborators** và có commit/PR hợp lệ vào repo.

---

## 8. CẤU HÌNH MÔI TRƯỜNG, MÃ NGUỒN LÕI & DEPLOY RENDER CLOUD

### 8.1. File cấu hình sẵn sàng

**`requirements.txt`:**
```text
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
psycopg[binary]>=3.2.0
python-dotenv>=1.0.1
passlib[bcrypt]>=1.7.4
PyJWT>=2.9.0
python-multipart>=0.0.12
websockets>=13.1
```

**`render.yaml`:**
```yaml
services:
  - type: web
    name: mxh-sinh-vien-ltm
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: ENV_MODE
        value: production
      - key: JWT_SECRET
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: mxh-sinh-vien-db
          property: connectionString

databases:
  - name: mxh-sinh-vien-db
    databaseName: mxh_sinh_vien
    user: mxh_admin
    plan: free
```

**`.env.example`:**
```dotenv
PORT=8000
SERVER_URL=https://mxh-sinh-vien-ltm.onrender.com
DATABASE_URL=postgresql://postgres:password@localhost:5432/mxh_sinh_vien
JWT_SECRET=doi-chuoi-bi-mat-tai-day
UPLOAD_DIR=./uploads
```

**`.gitignore`:**
```text
.venv/
venv/
__pycache__/
*.pyc
*.pyo
.env
.DS_Store
uploads/
```

### 8.2. Mã nguồn lõi khởi chạy (`server.py`, `client_app.py` & `src/Shared/`)

**`server.py`:**
```python
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
```

**`client_app.py`:**
```python
"""
App Desktop Client (Python Tkinter — KHÔNG phải trang Web)
Chạy trực tiếp trên máy tính sinh viên/giảng viên để kết nối tới Python Server trên Render.
"""
import json
import os
import tkinter as tk
from tkinter import ttk
import urllib.request

from dotenv import load_dotenv
from src.Modules.M01_Auth_TaiKhoan__TuAnh.Views.m01_view import Module01View

load_dotenv()
DEFAULT_SERVER = os.getenv("SERVER_URL", "http://127.0.0.1:8000")


class MxhDesktopClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mạng Xã Hội Sinh Viên — Python Desktop Client (MVC)")
        self.geometry("920x600")

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Server Cloud URL:").pack(side="left")
        self.url_var = tk.StringVar(value=DEFAULT_SERVER)
        ttk.Entry(top, textvariable=self.url_var, width=48).pack(side="left", padx=6)
        ttk.Button(top, text="Kiểm tra kết nối Server", command=self.check_server).pack(side="left")
        self.status_lbl = ttk.Label(top, text="Chưa kiểm tra", foreground="#64748b")
        self.status_lbl.pack(side="left", padx=10)

        ttk.Separator(self, orient="horizontal").pack(fill="x")
        self.content = Module01View(self, server_url=DEFAULT_SERVER)
        self.content.pack(fill="both", expand=True)

    def check_server(self):
        url = self.url_var.get().rstrip("/") + "/health"
        try:
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.status_lbl.config(text=f"Kết nối OK ({data.get('database')})", foreground="#15803d")
        except Exception as exc:
            self.status_lbl.config(text=f"Lỗi: {exc}", foreground="#dc2626")


if __name__ == "__main__":
    app = MxhDesktopClient()
    app.mainloop()
```

**`src/Shared/config/db.py`:**
```python
"""PostgreSQL database connection helper using psycopg3."""
import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "")


@contextmanager
def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("Chưa cấu hình biến môi trường DATABASE_URL cho PostgreSQL.")
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def check_db_health() -> dict:
    if not DATABASE_URL:
        return {"connected": False, "detail": "Chưa gắn DATABASE_URL"}
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*)::int AS total_tables FROM information_schema.tables WHERE table_schema = %s",
                ("public",),
            )
            row = cur.fetchone()
            return {"connected": True, "tables": row["total_tables"]}
    except Exception as exc:
        return {"connected": False, "detail": str(exc)}
```

**`src/Shared/middlewares/auth_middleware.py`:**
```python
"""JWT & NguoiDung verification helpers (Tú Anh - M01)."""
import os
from fastapi import Depends, HTTPException, Header
import jwt
from src.Shared.config.db import DATABASE_URL, get_conn

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-env")
JWT_ALG = "HS256"


def decode_and_validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Token không hợp lệ hoặc đã hết hạn: {exc}")

    if DATABASE_URL and payload.get("sub"):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT "TrangThai" AS user_status, "VaiTro" AS role_name
                FROM "NguoiDung"
                WHERE "MaNguoiDung" = %s
                """,
                (int(payload["sub"]),),
            )
            row = cur.fetchone()
            if not row or row["user_status"] != "HoatDong":
                raise HTTPException(status_code=401, detail="Tài khoản không hoạt động hoặc đã bị khóa.")
            payload["role"] = row["role_name"]
    return payload


def verify_token(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu Bearer Token xác thực.")
    return decode_and_validate_token(authorization[7:].strip())


def require_admin(user: dict = Depends(verify_token)) -> dict:
    if user.get("role") != "QuanTriVien":
        raise HTTPException(status_code=403, detail="Chỉ Quản trị viên (QuanTriVien) được phép thực hiện.")
    return user
```

**`src/Shared/middlewares/realtime_helper.py`:**
```python
"""WebSocket ConnectionManager & Realtime Push Helper (Thái - M09)."""
from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_clients: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_clients[str(user_id)] = websocket

    def disconnect(self, user_id: str) -> None:
        self.active_clients.pop(str(user_id), None)

    async def send_notification(self, user_id: str, event_type: str, payload: dict) -> bool:
        ws = self.active_clients.get(str(user_id))
        if ws is None:
            return False
        await ws.send_json({"event": event_type, "payload": payload})
        return True


manager = ConnectionManager()
```

### 8.3. Chạy thử trên máy cá nhân (Local)
```bash
# 1. Tạo môi trường ảo Python & cài thư viện
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 2. Tạo CSDL PostgreSQL & nạp đủ 18 bảng + dữ liệu mẫu
psql -U postgres -c "CREATE DATABASE mxh_sinh_vien;"
psql -U postgres -d mxh_sinh_vien -f database/01_schema_18_tables_postgres.sql
psql -U postgres -d mxh_sinh_vien -f database/02_seed_5_cap_truong.sql

# 3. Cấu hình biến môi trường & khởi chạy Server + Client
cp .env.example .env   # điền DATABASE_URL, JWT_SECRET
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Mở thêm 1 Terminal khác để chạy App Desktop Tkinter (KHÔNG phải Web):
python client_app.py
```

### 8.4. Đưa lên GitHub & Deploy Cloud Render
1. Đẩy toàn bộ dự án lên nhánh `main` của GitHub Repo nhóm.
2. Đăng nhập **Render.com** bằng tài khoản GitHub → chọn **New → Blueprint** → trỏ vào Repo GitHub (`render.yaml` tự động tạo Python Web Service `mxh-sinh-vien-ltm` + PostgreSQL Free `mxh-sinh-vien-db` và nối sẵn `DATABASE_URL`).
3. Lấy **External Database URL** trong trang PostgreSQL của Render để chạy 2 file SQL (`01_schema_18_tables_postgres.sql` và `02_seed_5_cap_truong.sql`).
4. Kiểm tra kết quả qua đường link Render (nộp trong báo cáo cuối kỳ):
   - `GET /`: Trang Server Monitor hiển thị trạng thái kết nối **PostgreSQL (18 bảng)**, số WebSocket Client online & 10 Module MVC.
   - `GET /health`: Trả JSON trạng thái Server & DB.
   - `GET /docs`: Tài liệu API Swagger tự sinh của FastAPI.
   - Chạy `python client_app.py` ở máy trạm, nhập link Render Cloud URL để App Desktop Tkinter kết nối trực tiếp lên Cloud Server.
