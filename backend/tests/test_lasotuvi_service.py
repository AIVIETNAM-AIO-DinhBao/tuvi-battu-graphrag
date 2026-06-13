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