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
