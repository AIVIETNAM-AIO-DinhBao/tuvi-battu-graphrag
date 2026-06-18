# -*- coding: utf-8 -*-
"""
Unit tests for Lasotuvi Service
"""

import pytest
from app.services.lasotuvi_service import LasoTuviService


class TestLasoTuviServiceValidation:
    """Test input validation"""

    def test_valid_input(self):
        """Test valid input passes validation"""
        is_valid, error = LasoTuviService.validate_input(
            ngay=15, thang=10, nam=1990, gio=6, gioi_tinh=1
        )
        assert is_valid is True
        assert error is None

    def test_invalid_ngay(self):
        """Test invalid day fails validation"""
        is_valid, error = LasoTuviService.validate_input(
            ngay=32, thang=10, nam=1990, gio=6, gioi_tinh=1
        )
        assert is_valid is False
        assert "Ngày sinh" in error

    def test_invalid_thang(self):
        """Test invalid month fails validation"""
        is_valid, error = LasoTuviService.validate_input(
            ngay=15, thang=13, nam=1990, gio=6, gioi_tinh=1
        )
        assert is_valid is False
        assert "Tháng sinh" in error

    def test_invalid_nam(self):
        """Test invalid year fails validation"""
        is_valid, error = LasoTuviService.validate_input(
            ngay=15, thang=10, nam=1800, gio=6, gioi_tinh=1
        )
        assert is_valid is False
        assert "Năm sinh" in error

    def test_invalid_gio(self):
        """Test invalid hour fails validation"""
        is_valid, error = LasoTuviService.validate_input(
            ngay=15, thang=10, nam=1990, gio=0, gioi_tinh=1
        )
        assert is_valid is False
        assert "Giờ sinh" in error

    def test_invalid_gioi_tinh(self):
        """Test invalid gender fails validation"""
        is_valid, error = LasoTuviService.validate_input(
            ngay=15, thang=10, nam=1990, gio=6, gioi_tinh=0
        )
        assert is_valid is False
        assert "Giới tính" in error

    def test_nu_gioi_tinh(self):
        """Test female gender passes validation"""
        is_valid, error = LasoTuviService.validate_input(
            ngay=15, thang=10, nam=1990, gio=6, gioi_tinh=-1
        )
        assert is_valid is True
        assert error is None


class TestLasoTuviServiceGenerate:
    """Test lá số generation"""

    @pytest.fixture
    def sample_la_so(self):
        """Generate a sample lá số for testing"""
        return LasoTuviService.generate_la_so(
            ngay=15, thang=10, nam=1990, gio=6, gioi_tinh=1
        )

    def test_generate_returns_dict(self, sample_la_so):
        """Test generate returns dictionary"""
        assert isinstance(sample_la_so, dict)

    def test_generate_contains_ngay_thang_nam(self, sample_la_so):
        """Test result contains date info"""
        assert sample_la_so['ngay'] == 15
        assert sample_la_so['thang'] == 10
        assert sample_la_so['nam'] == 1990

    def test_generate_contains_gio(self, sample_la_so):
        """Test result contains hour info"""
        assert sample_la_so['gio'] == 6

    def test_generate_contains_gioi_tinh(self, sample_la_so):
        """Test result contains gender info"""
        assert sample_la_so['gioiTinh'] == "Nam"

    def test_generate_contains_cung_menh(self, sample_la_so):
        """Test result contains cung menh"""
        assert 'cungMenh' in sample_la_so
        assert isinstance(sample_la_so['cungMenh'], int)
        assert 1 <= sample_la_so['cungMenh'] <= 12

    def test_generate_contains_cung_than(self, sample_la_so):
        """Test result contains cung than"""
        assert 'cungThan' in sample_la_so
        assert isinstance(sample_la_so['cungThan'], int)
        assert 1 <= sample_la_so['cungThan'] <= 12

    def test_generate_contains_thap_nhi_cung(self, sample_la_so):
        """Test result contains 12 cung"""
        assert 'thapNhiCung' in sample_la_so
        assert len(sample_la_so['thapNhiCung']) == 12

    def test_thap_nhi_cung_structure(self, sample_la_so):
        """Test each cung has required fields"""
        for cung in sample_la_so['thapNhiCung']:
            assert 'cungSo' in cung
            assert 'cungTen' in cung
            assert 'cungChu' in cung
            assert 'hanhCung' in cung
            assert 'amDuong' in cung
            assert 'cungSao' in cung
            assert isinstance(cung['cungSao'], list)

    def test_generate_invalid_input_raises(self):
        """Test invalid input raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LasoTuviService.generate_la_so(
                ngay=32, thang=10, nam=1990, gio=6, gioi_tinh=1
            )
        assert "Ngày sinh" in str(exc_info.value)


class TestLasoTuviServiceHelpers:
    """Test helper methods"""

    @pytest.fixture
    def sample_la_so(self):
        """Generate a sample lá số for testing"""
        return LasoTuviService.generate_la_so(
            ngay=15, thang=10, nam=1990, gio=6, gioi_tinh=1
        )

    def test_get_cung_info_valid(self, sample_la_so):
        """Test get_cung_info with valid cung number"""
        cung_info = LasoTuviService.get_cung_info(sample_la_so, 1)
        assert cung_info is not None
        assert cung_info['cungSo'] == 1

    def test_get_cung_info_invalid(self, sample_la_so):
        """Test get_cung_info with invalid cung number"""
        cung_info = LasoTuviService.get_cung_info(sample_la_so, 15)
        assert cung_info is None

    def test_get_sao_in_cung(self, sample_la_so):
        """Test get_sao_in_cung returns list"""
        sao_list = LasoTuviService.get_sao_in_cung(sample_la_so, 1)
        assert isinstance(sao_list, list)

    def test_format_for_output(self, sample_la_so):
        """Test format_for_output returns structured dict"""
        formatted = LasoTuviService.format_for_output(sample_la_so)
        
        assert 'thongTinCanChi' in formatted
        assert 'daiCung' in formatted
        assert 'thapNhiCung' in formatted
        
        assert formatted['thongTinCanChi']['ngay'] == 15
        assert formatted['thongTinCanChi']['thang'] == 10
        assert formatted['thongTinCanChi']['nam'] == 1990


class TestLasoTuViServiceExtendedMetadata:
    """Test additive metadata helpers without requiring the lasotuvi package."""

    def test_brightness_code_normalization(self):
        assert LasoTuviService._brightness_code("Vượng") == "V"
        assert LasoTuviService._brightness_code("Đắc") == "Đ"
        assert LasoTuviService._brightness_code("Hãm") == "H"
        assert LasoTuviService._brightness_code("Miếu") == "M"
        assert LasoTuviService._brightness_code("Bình") == "B"

    def test_year_can_chi_and_nap_am(self):
        assert LasoTuviService._get_can_chi_year(1990) == "Canh Ngọ"
        assert LasoTuviService._get_nap_am("Canh Ngọ") == "Lộ Bàng Thổ"

    def test_star_category_accepts_string_ids(self):
        assert LasoTuviService._star_category(None, "1") == "Chính tinh"

    def test_lunar_date_fallback_converter(self):
        lunar_date = LasoTuviService._convert_solar_to_lunar(15, 10, 1990, 7)

        assert lunar_date["day"] == 27
        assert lunar_date["month"] == 8
        assert lunar_date["year"] == 1990
        assert LasoTuviService._calculate_can_luong(1990, lunar_date, 6) == "4 luong 7 chi"

    def test_star_quality_normalization(self):
        assert LasoTuviService._star_quality("Địa Không") == "sat_tinh"
        assert LasoTuviService._star_quality("Thiên Khôi") == "cat_tinh"
        assert LasoTuviService._star_quality("L.Thiên Mã") == "sat_tinh"
        assert LasoTuviService._star_quality("Thái Tuế") == "sat_tinh"
        assert LasoTuviService._star_quality("L.Thái Tuế") == "sat_tinh"
        assert LasoTuviService._star_quality("Phi Liêm") == "sat_tinh"
        assert LasoTuviService._star_quality("Thiên Không") == "sat_tinh"
        assert LasoTuviService._star_quality("Lưu Hà") == "sat_tinh"
        assert LasoTuviService._star_quality("Thiên La") == "sat_tinh"
        assert LasoTuviService._star_quality("Địa Võng") == "sat_tinh"

    def test_trang_sinh_moc_tam_cuc_starts_at_hoi(self):
        cycle = LasoTuviService._build_trang_sinh_by_position("Moc tam cuc", 1990, 1)

        assert cycle[12] == LasoTuviService.TRANG_SINH[0]
        assert cycle[1] == LasoTuviService.TRANG_SINH[1]

    def test_cuc_menh_uses_ngu_ho_don_can_chi(self):
        assert LasoTuviService._get_cung_can_chi(2005, 4) == "Kỷ Mão"
        assert LasoTuviService._infer_cuc_menh(2005, 4) == "Thổ ngũ cục"

    def test_am_duong_ly(self):
        assert LasoTuviService._calculate_am_duong_ly("Âm Nam", 4) == "Thuận lý"
        assert LasoTuviService._calculate_am_duong_ly("Dương Nam", 4) == "Nghịch lý"
        assert LasoTuviService._calculate_am_duong_ly("Dương Nam", 3) == "Thuận lý"
        assert LasoTuviService._calculate_am_duong_ly("Âm Nữ", 3) == "Thuận lý"

    @pytest.mark.parametrize(
        "menh,cuc,expected",
        [
            ("Hỏa", "Mộc", "Cục sinh Mệnh"),
            ("Mộc", "Hỏa", "Mệnh sinh Cục"),
            ("Thủy", "Thổ", "Cục khắc Mệnh"),
            ("Mộc", "Thổ", "Mệnh khắc Cục"),
            ("Kim", "Kim", "Mệnh - Cục bình hòa"),
        ],
    )
    def test_menh_cuc_relation(self, menh, cuc, expected):
        assert LasoTuviService._calculate_menh_cuc_relation(menh, cuc) == expected

    def test_filters_engine_trang_sinh_stars(self):
        assert LasoTuviService._is_trang_sinh_star("Tràng sinh") is True
        assert LasoTuviService._is_trang_sinh_star("Thiên Khôi") is False

    @pytest.mark.parametrize(
        "birth_branch,hoa_start,linh_start",
        [
            (3, 2, 4),
            (1, 3, 11),
            (10, 4, 11),
            (4, 10, 11),
        ],
    )
    def test_hoa_linh_uses_standard_group_table(self, birth_branch, hoa_start, linh_start):
        assert LasoTuviService._calculate_hoa_linh_positions(2006, birth_branch, 3, 1) == (
            LasoTuviService._shift_branch(hoa_start, 2),
            LasoTuviService._shift_branch(linh_start, -2),
        )
        assert LasoTuviService._calculate_hoa_linh_positions(2006, birth_branch, 3, -1) == (
            LasoTuviService._shift_branch(hoa_start, -2),
            LasoTuviService._shift_branch(linh_start, 2),
        )

    def test_pha_toai_for_dau_year_goes_to_ty_branch(self):
        dau_branch = 10
        assert LasoTuviService._calculate_pha_toai_position(dau_branch) == 6

    def test_an_sao_luu_for_binh_ngo_2026(self):
        placements = {
            item["name"]: item["position"]
            for item in LasoTuviService.an_sao_luu("Bính", "Ngọ", 2026)
        }

        assert placements["L.Thái Tuế"] == 7
        assert placements["L.Tang Môn"] == 9
        assert placements["L.Bạch Hổ"] == 3
        assert placements["L.Lộc Tồn"] == 6
        assert placements["L.Kình Dương"] == 7
        assert placements["L.Đà La"] == 5
        assert placements["L.Thiên Mã"] == 9

    def test_star_brightness_overrides(self):
        assert LasoTuviService._resolve_star_brightness("Văn Khúc", 4)["code"] == "H"
        assert LasoTuviService._resolve_star_brightness("Hóa Quyền", 1)["code"] == "V"
        assert LasoTuviService._resolve_star_brightness("Hóa Lộc", 1)["code"] == "Đ"
        assert LasoTuviService._resolve_star_brightness("Hóa Khoa", 1)["code"] == "Đ"
        assert LasoTuviService._resolve_star_brightness("Hóa Kỵ", 1)["code"] == "H"
        assert LasoTuviService._resolve_star_brightness("L.Lộc Tồn", 1)["code"] == "M"
        assert LasoTuviService._resolve_star_brightness("L.Thiên Mã", 1)["code"] == "H"

    def test_triet_positions_by_birth_stem(self):
        assert LasoTuviService._calculate_triet_positions("Ất") == [7, 8]
        assert LasoTuviService._calculate_triet_positions("Giáp") == [9, 10]
        assert LasoTuviService._calculate_triet_positions("Bính") == [5, 6]
        assert LasoTuviService._calculate_triet_positions("Đinh") == [3, 4]
        assert LasoTuviService._calculate_triet_positions("Mậu") == [1, 2]

    @pytest.mark.parametrize(
        "can_chi,expected",
        [
            ("Giáp Tý", [11, 12]),
            ("Giáp Tuất", [9, 10]),
            ("Giáp Thân", [7, 8]),
            ("Giáp Ngọ", [5, 6]),
            ("Giáp Thìn", [3, 4]),
            ("Giáp Dần", [1, 2]),
            ("Ất Dậu", [7, 8]),
        ],
    )
    def test_tuan_positions_by_luc_thap_hoa_giap_week(self, can_chi, expected):
        assert LasoTuviService._calculate_tuan_positions(can_chi) == expected

    def test_generate_applies_v6_corrected_and_annual_stars(self):
        result = LasoTuviService.generate_la_so(
            ngay=1,
            thang=1,
            nam=2005,
            gio=10,
            gioi_tinh=1,
            nam_xem_han=2026,
        )

        by_role = {cung["cungChu"]: cung for cung in result["thapNhiCung"]}

        assert result["namXemHan"] == 2026
        assert result["canChiNamXem"] == "Bính Ngọ"
        assert result["cungMenh"] == 4
        assert result["destinyInfo"]["banMenh"] == "Tuyền Trung Thủy"
        assert result["destinyInfo"]["cucMenh"] == "Thổ ngũ cục"
        assert result["destinyInfo"]["menhNguHanh"] == "Thủy"
        assert result["destinyInfo"]["cucNguHanh"] == "Thổ"
        assert result["destinyInfo"]["amDuongLy"] == "Thuận lý"
        assert result["destinyInfo"]["menhCucTuongQuan"] == "Cục khắc Mệnh"
        assert "Phá Toái" in [s["saoTen"] for s in by_role["Phúc đức"]["cungSao"]]
        assert {"L.Lộc Tồn", "Phá Toái"}.issubset(
            {s["saoTen"] for s in by_role["Phúc đức"]["cungSao"]}
        )
        assert {"L.Thái Tuế", "L.Kình Dương"}.issubset(
            {s["saoTen"] for s in by_role["Điền trạch"]["cungSao"]}
        )
        assert "L.Đà La" in {s["saoTen"] for s in by_role["Phụ mẫu"]["cungSao"]}
        assert {"L.Thiên Mã", "L.Tang Môn"}.issubset(
            {s["saoTen"] for s in by_role["Nô bộc"]["cungSao"]}
        )
        assert all(
            s.get("is_luu") is True
            for cung in result["thapNhiCung"]
            for s in cung["cungSao"]
            if s["saoTen"].startswith("L.")
        )

    def test_generate_marks_tuan_triet_without_adding_them_as_stars(self):
        result = LasoTuviService.generate_la_so(
            ngay=1,
            thang=1,
            nam=2005,
            gio=10,
            gioi_tinh=1,
            nam_xem_han=2026,
        )

        by_position = {cung["cungSo"]: cung for cung in result["thapNhiCung"]}
        for position in [7, 8]:
            assert by_position[position]["tuanKhong"] is True
            assert by_position[position]["trietKhong"] is True
            assert by_position[position]["khongVong"] == ["Tuần", "Triệt"]

        void_star_names = {"tuan", "triet", "tuan khong", "triet khong"}
        assert not any(
            LasoTuviService._normalize_text(star["saoTen"]) in void_star_names
            for cung in result["thapNhiCung"]
            for star in cung["cungSao"]
        )

    def test_format_for_output_includes_extended_metadata(self):
        raw_chart = {
            "ngay": 15,
            "thang": 10,
            "nam": 1990,
            "gio": 6,
            "gioiTinh": "Nam",
            "duongLich": True,
            "personalInfo": {"gender": "Nam"},
            "destinyInfo": {"banMenh": "Lộ Bàng Thổ"},
            "cungMenh": 5,
            "cungThan": 11,
            "tenCungMenh": "Thìn",
            "tenCungThan": "Tuất",
            "thapNhiCung": [],
            "namXemHan": 2026,
            "canChiNamXem": "Bính Ngọ",
            "lunarDate": {"day": 27, "month": 8, "year": 1990},
            "timestamp": "2026-06-17T00:00:00",
        }

        formatted = LasoTuviService.format_for_output(raw_chart)

        assert formatted["thongTinCanChi"]["personalInfo"]["gender"] == "Nam"
        assert formatted["thongTinCanChi"]["destinyInfo"]["banMenh"] == "Lộ Bàng Thổ"
        assert formatted["thongTinCanChi"]["namXemHan"] == 2026
        assert formatted["thongTinCanChi"]["canChiNamXem"] == "Bính Ngọ"
        assert formatted["lunarDate"]["year"] == 1990
        assert formatted["timestamp"] == "2026-06-17T00:00:00"


class TestLasoTuviServiceEdgeCases:
    """Test edge cases"""

    def test_boundary_ngay_1(self):
        """Test day = 1 (boundary)"""
        result = LasoTuviService.generate_la_so(
            ngay=1, thang=1, nam=2000, gio=1, gioi_tinh=1
        )
        assert result['ngay'] == 1

    def test_boundary_ngay_31(self):
        """Test day = 31 (boundary)"""
        result = LasoTuviService.generate_la_so(
            ngay=31, thang=12, nam=2000, gio=12, gioi_tinh=-1
        )
        assert result['ngay'] == 31

    def test_boundary_nam_1900(self):
        """Test year = 1900 (boundary)"""
        result = LasoTuviService.generate_la_so(
            ngay=1, thang=1, nam=1900, gio=1, gioi_tinh=1
        )
        assert result['nam'] == 1900

    def test_boundary_nam_2100(self):
        """Test year = 2100 (boundary)"""
        result = LasoTuviService.generate_la_so(
            ngay=1, thang=1, nam=2100, gio=1, gioi_tinh=1
        )
        assert result['nam'] == 2100

    def test_all_gio_values(self):
        """Test all 12 gio (hour) values"""
        for gio in range(1, 13):
            result = LasoTuviService.generate_la_so(
                ngay=15, thang=6, nam=2000, gio=gio, gioi_tinh=1
            )
            assert result['gio'] == gio
