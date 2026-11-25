# M1 — Tài khoản, Hồ sơ & Quên mật khẩu (OTP)

- **Thành viên sở hữu (End-to-End):** Nguyễn Ngô Tú Anh (Leader)
- **Thư mục MVC:** `src/Modules/M01_Auth_TaiKhoan__TuAnh`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `NguoiDung`
- **Endpoints / WebSocket dự kiến:**
  - `POST /api/m01/auth/register`
  - `POST /api/m01/auth/login`
  - `POST /api/m01/auth/logout`
  - `PUT /api/m01/users/password`
  - `POST /api/m01/auth/forgot-otp`
  - `POST /api/m01/auth/reset-pw`
  - `PUT /api/m01/users/profile`

## Phạm vi chức năng
Đăng ký theo lớp (cấp MaLop trỏ cây CongDong), Đăng nhập JWT (theo VaiTro trong NguoiDung), Đăng xuất, Đổi mật khẩu, Quên MK qua MaOTP/HanOTP, Cập nhật hồ sơ & Đổi lớp.

## Quy trình 4 Bước hoàn thành
- **B1 (Base Python MVC & DB):** Dựng FastAPI, Tkinter Client & kết nối PostgreSQL psycopg vào bảng NguoiDung.
- **B2 (Controller & Middleware):** Code m01_controller.py & auth_middleware.py xác thực JWT và kiểm tra TrangThai trong NguoiDung.
- **B3 (Tkinter Desktop View):** Dựng Frame Đăng ký (chọn Trường→Lớp từ M02), Đăng nhập, Quên MK OTP & Hồ sơ.
- **B4 (Demo & KPI):** Test trọn luồng từ Tkinter Client: Đăng ký → Đăng nhập → Quên MK OTP → Đổi MK / Cập nhật hồ sơ.

**KPI:** Deploy Render ổn định, Tkinter Client đăng ký/đăng nhập/đổi lớp mượt mà trên bảng NguoiDung.
