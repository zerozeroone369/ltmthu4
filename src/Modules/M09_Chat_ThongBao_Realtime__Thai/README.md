# M9 — Nhắn tin Realtime & Thông báo

- **Thành viên sở hữu (End-to-End):** Thái (UI Lead)
- **Thư mục MVC:** `src/Modules/M09_Chat_ThongBao_Realtime__Thai`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `TinNhan`, `ThongBao`
- **Endpoints / WebSocket dự kiến:**
  - `GET /api/m09/chat/history`
  - `POST /api/m09/chat/send`
  - `GET /api/m09/notifications`
  - `PUT /api/m09/notifications/{id}/read`
  - `WS /ws (chat_message, notification)`

## Phạm vi chức năng
Mở kênh WebSocket /ws cho phép nhắn tin 1-1 và chat nhóm trực tiếp (lưu lịch sử TinNhan); Chuông thông báo & hộp thư ThongBao; cung cấp hàm send_notification() cho Duy, Huy, Bảo đẩy thông báo tức thì.

## Quy trình 4 Bước hoàn thành
- **B1 (Model TinNhan & ThongBao):** Tạo Model cho TinNhan (chat 1-1 & chat nhóm) và ThongBao; chốt hàm send_notification() dùng chung.
- **B2 (WebSocket Server /ws):** Quản lý danh sách user đang kết nối WebSocket, kiểm tra chặn trước khi gửi tin và lưu DB khi user offline.
- **B3 (Tkinter Chat & Chuông TB):** Dựng khung chat hai chiều và chuông thông báo hiển thị tin mới ngay lập tức trên App Desktop.
- **B4 (Demo & KPI):** Mở 2 cửa sổ App Desktop Tkinter nối chung Server Render test nhắn tin 1-1, chat nhóm và chuông thông báo.

**KPI:** Tin nhắn và thông báo hiển thị tức thì khi hai máy cùng mở app, không mất tin khi đối phương offline.
