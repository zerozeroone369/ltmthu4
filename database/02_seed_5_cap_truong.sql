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
