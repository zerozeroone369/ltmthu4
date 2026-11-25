# M5 — Hỏi đáp Học thuật (Q&A & Upvote)

- **Thành viên sở hữu (End-to-End):** Huy (Full-stack Module)
- **Thư mục MVC:** `src/Modules/M05_HoiDap_QA__Huy`
- **Ngôn ngữ:** Python 3 (FastAPI Controller + PostgreSQL `psycopg` Model + Tkinter Desktop View)
- **Bảng PostgreSQL (trong 18 bảng tinh gọn):** `CauHoi`, `CauTraLoi`, `BinhChonCauTraLoi`
- **Endpoints / WebSocket dự kiến:**
  - `CRUD /api/m05/questions`
  - `POST /api/m05/questions/{id}/answers`
  - `POST /api/m05/answers/{id}/upvote`
  - `PUT /api/m05/answers/{id}/correct`

## Phạm vi chức năng
Đặt câu hỏi theo MonHoc kèm từ khóa TheTuKhoa (#Socket, #SQL, #Python); Gửi câu trả lời; Bấm Upvote hữu ích (1 lần/người qua BinhChonCauTraLoi); Chủ câu hỏi chốt Đáp án đúng.

## Quy trình 4 Bước hoàn thành
- **B1 (Model 3 bảng Q&A):** Tạo Model cho CauHoi (có cột TheTuKhoa, DaGiaiQuyet), CauTraLoi và BinhChonCauTraLoi.
- **B2 (Controller Q&A):** Viết API tạo câu hỏi, trả lời (gọi thông báo cho tác giả), toggle Upvote và chốt Đáp án đúng.
- **B3 (Tkinter Desktop View):** Dựng danh sách câu hỏi, ô lọc theo Môn/#Thẻ, nút Upvote & nút Chốt đáp án cho tác giả.
- **B4 (Demo & KPI):** Test trọn luồng đặt câu hỏi → bạn trả lời → cộng đồng Upvote → tác giả chốt đáp án đúng.

**KPI:** Không vote trùng trên 1 câu trả lời, đáp án đúng được ghim nổi bật lên đầu danh sách.
