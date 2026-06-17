# -*- coding: utf-8 -*-
"""
Lasotuvi Service - Wrapper around lasotuvi engine for Tử Vi calculations
Provides structured interface for generating Tử Vi lá số (birth chart)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import math
import logging
import unicodedata

logger = logging.getLogger(__name__)


class LasoTuviService:
    """Service for generating Tử Vi birth charts using lasotuvi engine"""

    DIA_CHI = [
        "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
        "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
    ]
    THIEN_CAN = [
        "Giáp", "Ất", "Bính", "Đinh", "Mậu",
        "Kỷ", "Canh", "Tân", "Nhâm", "Quý"
    ]
    HOUR_RANGES = {
        1: "23h-01h", 2: "01h-03h", 3: "03h-05h", 4: "05h-07h",
        5: "07h-09h", 6: "09h-11h", 7: "11h-13h", 8: "13h-15h",
        9: "15h-17h", 10: "17h-19h", 11: "19h-21h", 12: "21h-23h",
    }
    TRANG_SINH = [
        "Tràng sinh", "Mộc dục", "Quan đới", "Lâm quan",
        "Đế vượng", "Suy", "Bệnh", "Tử", "Mộ",
        "Tuyệt", "Thai", "Dưỡng"
    ]
    CHINH_TINH_IDS = set(range(1, 15))
    CHINH_TINH_NAMES = {
        "tử vi", "thiên cơ", "thái dương", "vũ khúc", "thiên đồng",
        "liêm trinh", "thiên phủ", "thái âm", "tham lang", "cự môn",
        "thiên tướng", "thiên lương", "thất sát", "phá quân",
    }
    NAP_AM_BY_CAN_CHI = {
        "Giáp Tý": "Hải Trung Kim", "Ất Sửu": "Hải Trung Kim",
        "Bính Dần": "Lư Trung Hỏa", "Đinh Mão": "Lư Trung Hỏa",
        "Mậu Thìn": "Đại Lâm Mộc", "Kỷ Tỵ": "Đại Lâm Mộc",
        "Canh Ngọ": "Lộ Bàng Thổ", "Tân Mùi": "Lộ Bàng Thổ",
        "Nhâm Thân": "Kiếm Phong Kim", "Quý Dậu": "Kiếm Phong Kim",
        "Giáp Tuất": "Sơn Đầu Hỏa", "Ất Hợi": "Sơn Đầu Hỏa",
        "Bính Tý": "Giản Hạ Thủy", "Đinh Sửu": "Giản Hạ Thủy",
        "Mậu Dần": "Thành Đầu Thổ", "Kỷ Mão": "Thành Đầu Thổ",
        "Canh Thìn": "Bạch Lạp Kim", "Tân Tỵ": "Bạch Lạp Kim",
        "Nhâm Ngọ": "Dương Liễu Mộc", "Quý Mùi": "Dương Liễu Mộc",
        "Giáp Thân": "Tuyền Trung Thủy", "Ất Dậu": "Tuyền Trung Thủy",
        "Bính Tuất": "Ốc Thượng Thổ", "Đinh Hợi": "Ốc Thượng Thổ",
        "Mậu Tý": "Tích Lịch Hỏa", "Kỷ Sửu": "Tích Lịch Hỏa",
        "Canh Dần": "Tùng Bách Mộc", "Tân Mão": "Tùng Bách Mộc",
        "Nhâm Thìn": "Trường Lưu Thủy", "Quý Tỵ": "Trường Lưu Thủy",
        "Giáp Ngọ": "Sa Trung Kim", "Ất Mùi": "Sa Trung Kim",
        "Bính Thân": "Sơn Hạ Hỏa", "Đinh Dậu": "Sơn Hạ Hỏa",
        "Mậu Tuất": "Bình Địa Mộc", "Kỷ Hợi": "Bình Địa Mộc",
        "Canh Tý": "Bích Thượng Thổ", "Tân Sửu": "Bích Thượng Thổ",
        "Nhâm Dần": "Kim Bạch Kim", "Quý Mão": "Kim Bạch Kim",
        "Giáp Thìn": "Phú Đăng Hỏa", "Ất Tỵ": "Phú Đăng Hỏa",
        "Bính Ngọ": "Thiên Hà Thủy", "Đinh Mùi": "Thiên Hà Thủy",
        "Mậu Thân": "Đại Dịch Thổ", "Kỷ Dậu": "Đại Dịch Thổ",
        "Canh Tuất": "Thoa Xuyến Kim", "Tân Hợi": "Thoa Xuyến Kim",
        "Nhâm Tý": "Tang Đố Mộc", "Quý Sửu": "Tang Đố Mộc",
        "Giáp Dần": "Đại Khê Thủy", "Ất Mão": "Đại Khê Thủy",
        "Bính Thìn": "Sa Trung Thổ", "Đinh Tỵ": "Sa Trung Thổ",
        "Mậu Ngọ": "Thiên Thượng Hỏa", "Kỷ Mùi": "Thiên Thượng Hỏa",
        "Canh Thân": "Thạch Lựu Mộc", "Tân Dậu": "Thạch Lựu Mộc",
        "Nhâm Tuất": "Đại Hải Thủy", "Quý Hợi": "Đại Hải Thủy",
    }

    CHU_MENH_BY_BRANCH_INDEX = [
        "Tham Lang", "Cu Mon", "Loc Ton", "Van Khuc",
        "Liem Trinh", "Vu Khuc", "Pha Quan", "Vu Khuc",
        "Liem Trinh", "Van Khuc", "Loc Ton", "Cu Mon",
    ]
    CHU_THAN_BY_BRANCH_INDEX = [
        "Linh Tinh", "Thien Tuong", "Thien Luong", "Thien Dong",
        "Van Xuong", "Thien Co", "Hoa Tinh", "Thien Tuong",
        "Thien Luong", "Thien Dong", "Van Xuong", "Thien Co",
    ]
    CUC_BY_ELEMENT = {
        "thuy": "Thuy nhi cuc",
        "moc": "Moc tam cuc",
        "kim": "Kim tu cuc",
        "tho": "Tho ngu cuc",
        "hoa": "Hoa luc cuc",
    }
    CAN_LUONG_YEAR_WEIGHTS = [
        12, 9, 6, 7, 12, 5, 9, 8, 7, 8,
        15, 9, 16, 8, 8, 19, 12, 6, 8, 7,
        5, 15, 6, 16, 15, 7, 9, 12, 10, 7,
        15, 6, 5, 14, 14, 9, 7, 7, 9, 12,
        8, 7, 13, 5, 14, 5, 9, 17, 5, 7,
        12, 8, 8, 6, 19, 6, 8, 16, 10, 6,
    ]
    CAN_LUONG_MONTH_WEIGHTS = [6, 7, 18, 9, 5, 16, 9, 15, 18, 8, 9, 5]
    CAN_LUONG_DAY_WEIGHTS = [
        5, 10, 8, 15, 16, 15, 8, 16, 8, 16,
        9, 17, 8, 17, 10, 8, 9, 18, 5, 15,
        10, 9, 8, 9, 15, 18, 7, 8, 16, 6,
    ]
    CAN_LUONG_HOUR_WEIGHTS = [16, 6, 7, 10, 9, 16, 10, 8, 8, 9, 6, 6]
    CAT_TINH_NAMES = {
        # Nhóm Cát tinh chủ chốt
        "thien khoi", "thien viet", "thien quy", "ta phu", "huu bat",
        # Nhóm Văn tinh
        "van xuong", "van khuc", "long tri", "phuong cac", "hoa cai",
        # Nhóm Quý tinh & Phúc tinh
        "thien quan", "thien phuc", "thien duc", "nguyet duc", "an quang", 
        "thien giai", "dia giai", "giai than", "phuc duc", "thien tru",
        # Nhóm Tài lộc & May mắn
        "hoa loc", "hoa quyen", "hoa khoa", "loc ton", "bat toa", "tam thai",
        # Nhóm Đào hoa & Hỷ sự
        "dao hoa", "hong loan", "hy than", "thien tai", "thien tho", "duong phu",
        "thien y", "phong cao", "thai phu",
    }

    SAT_TINH_NAMES = {
        # Nhóm Lục sát tinh
        "dia khong", "dia kiep", "kinh duong", "da la", "hoa tinh", "linh tinh",
        # Nhóm Bại tinh & Sát tinh khác
        "kiep sat", "thien hinh", "thien rieu", "thien dieu", "pha toai",
        # Nhóm Hao tinh
        "dai hao", "tieu hao",
        # Nhóm Tang - Hổ - Khốc - Hư (Bộ sao thị phi/buồn phiền)
        "tang mon", "bach ho", "thien khoc", "thien hu",
        # Nhóm Cô quả
        "co than", "qua tu",
        # Nhóm sao Vòng Thái Tuế / Lộc Tồn (tùy vị trí nhưng thường xét tính sát)
        "hoa ky", "phuc binh", "dieu khach", "benh phu", "truc phu", "dau quan", 
        "thien thuong", "thien su", "quan phu", "tu phu", "tu tuyet"
    }

    @staticmethod
    def validate_input(ngay: int, thang: int, nam: int, gio: int, gioi_tinh: int) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters for Tử Vi calculation
        
        Args:
            ngay: Day of birth (1-31)
            thang: Month of birth (1-12)
            nam: Year of birth (1900-2100)
            gio: Hour of birth (1-12, where 1=Tý, 2=Sửu, ..., 12=Hợi)
            gioi_tinh: Gender (1=Nam/Male, -1=Nữ/Female)
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not 1 <= ngay <= 31:
            return False, f"Ngày sinh phải trong khoảng 1-31, nhận được: {ngay}"
        
        if not 1 <= thang <= 12:
            return False, f"Tháng sinh phải trong khoảng 1-12, nhận được: {thang}"
        
        if not 1900 <= nam <= 2100:
            return False, f"Năm sinh phải trong khoảng 1900-2100, nhận được: {nam}"
        
        if not 1 <= gio <= 12:
            return False, f"Giờ sinh phải trong khoảng 1-12, nhận được: {gio}"
        
        if gioi_tinh not in [1, -1]:
            return False, f"Giới tính phải là 1 (Nam) hoặc -1 (Nữ), nhận được: {gioi_tinh}"
        
        return True, None

    @staticmethod
    def generate_la_so(
        ngay: int,
        thang: int,
        nam: int,
        gio: int,
        gioi_tinh: int,
        duong_lich: bool = True,
        time_zone: int = 7
    ) -> Dict[str, Any]:
        """
        Generate Tử Vi birth chart (lá số) from given birth date/time
        
        Args:
            ngay: Day of birth
            thang: Month of birth
            nam: Year of birth
            gio: Hour of birth (1-12)
            gioi_tinh: Gender (1=Nam, -1=Nữ)
            duong_lich: True if using Gregorian calendar (default), False if using lunar calendar
            time_zone: Timezone offset (default 7 for Vietnam)
        
        Returns:
            Dict containing complete birth chart information
        
        Raises:
            ValueError: If input validation fails
            Exception: If lasotuvi engine fails
        """
        try:
            # Validate input
            is_valid, error_msg = LasoTuviService.validate_input(ngay, thang, nam, gio, gioi_tinh)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Import lasotuvi modules
            from lasotuvi.DiaBan import diaBan
            from lasotuvi.App import lapDiaBan
            
            logger.info(f"Generating lá số for {ngay}/{thang}/{nam} {gio}h, giới tính: {'Nam' if gioi_tinh == 1 else 'Nữ'}")
            
            # Generate địa bàn (birth chart)
            dia_ban_obj = lapDiaBan(
                diaBan=diaBan,  # Pass class, not instance
                nn=ngay,
                tt=thang,
                nnnn=nam,
                gioSinh=gio,
                gioiTinh=gioi_tinh,
                duongLich=duong_lich,
                timeZone=time_zone
            )
            
            # Parse and structure the output
            result = LasoTuviService._parse_dia_ban(
                dia_ban_obj, ngay, thang, nam, gio, gioi_tinh, duong_lich, time_zone
            )
            
            logger.info("✓ Successfully generated lá số")
            return result
            
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error generating lá số: {str(e)}", exc_info=True)
            raise Exception(f"Lỗi khi sinh lá số: {str(e)}") from e

    @staticmethod
    def _parse_dia_ban(
        dia_ban_obj: Any,
        ngay: int,
        thang: int,
        nam: int,
        gio: int,
        gioi_tinh: int,
        duong_lich: bool = True,
        time_zone: int = 7,
    ) -> Dict[str, Any]:
        """
        Parse lasotuvi output into structured format
        
        Args:
            dia_ban_obj: Output object from lapDiaBan()
            ngay, thang, nam, gio, gioi_tinh: Birth information
        
        Returns:
            Structured dictionary with birth chart data
        """
        try:
            # Extract basic info
            cung_menh = dia_ban_obj.cungMenh
            cung_than = dia_ban_obj.cungThan
            can_chi_nam = LasoTuviService._get_can_chi_year(nam)
            lunar_date = LasoTuviService._get_lunar_date(
                dia_ban_obj, ngay, thang, nam, duong_lich, time_zone
            )
            personal_info = LasoTuviService._build_personal_info(
                dia_ban_obj=dia_ban_obj,
                ngay=ngay,
                thang=thang,
                nam=nam,
                gio=gio,
                gioi_tinh=gioi_tinh,
                duong_lich=duong_lich,
                time_zone=time_zone,
                can_chi_nam=can_chi_nam,
                lunar_date=lunar_date,
            )
            destiny_info = LasoTuviService._build_destiny_info(
                dia_ban_obj=dia_ban_obj,
                cung_menh=cung_menh,
                cung_than=cung_than,
                can_chi_nam=can_chi_nam,
                nam=nam,
                gio=gio,
                lunar_date=lunar_date,
            )
            
            # Process 12 cung (palaces)
            thap_nhi_cung = []
            for i in range(1, 13):  # Start from 1, skip index 0
                cung = dia_ban_obj.thapNhiCung[i]
                
                # Extract sao (stars) in this cung
                danh_sach_sao = []
                if hasattr(cung, 'cungSao') and cung.cungSao:
                    for sao in cung.cungSao:
                        sao_ten = sao.get('saoTen', 'Không rõ tên')
                        dac_tinh = sao.get('saoDacTinh')
                        sao_id = sao.get('saoID')
                        sao_info = {
                            'saoTen': sao.get('saoTen', 'Không rõ tên'),
                            'saoDacTinh': dac_tinh,
                            'saoDacTinhCode': LasoTuviService._brightness_code(dac_tinh),
                            'saoNhom': LasoTuviService._star_category(sao_ten, sao_id),
                            'saoTinhChat': LasoTuviService._star_quality(sao_ten),
                            'saoColor': LasoTuviService._brightness_color(dac_tinh),
                            'saoID': sao_id
                        }
                        danh_sach_sao.append(sao_info)
                
                # Get cung properties
                cung_chu = getattr(cung, 'cungChu', 'N/A')
                dai_han = getattr(cung, 'cungDaiHan', None)
                tieu_han = getattr(cung, 'cungTieuHan', None)
                dia_chi = getattr(cung, 'cungTen', None) or LasoTuviService._dia_chi_for_position(i)
                co_than = getattr(cung, 'cungThan', False)
                am_duong = 'Dương' if cung.cungAmDuong == 1 else 'Âm'
                
                cung_data = {
                    'cungSo': cung.cungSo,
                    'cungTen': cung.cungTen,
                    'diaChi': dia_chi,
                    'cungChu': cung_chu,
                    'hanhCung': cung.hanhCung,
                    'amDuong': am_duong,
                    'daiHan': dai_han,
                    'tuoiDaiHan': dai_han,
                    'tieuHan': tieu_han,
                    'luuNienDaiVan': LasoTuviService._get_attr(
                        cung, ['cungLuuNienDaiVan', 'luuNienDaiVan', 'lnDaiVan']
                    ),
                    'trangSinh': LasoTuviService._get_trang_sinh(cung, i),
                    'coThan': co_than,
                    'coThhan': co_than,
                    'cungSao': danh_sach_sao
                }
                
                thap_nhi_cung.append(cung_data)
            
            # Build final result
            result = {
                'ngay': ngay,
                'thang': thang,
                'nam': nam,
                'gio': gio,
                'duongLich': duong_lich,
                'timeZone': time_zone,
                'gioiTinh': 'Nam' if gioi_tinh == 1 else 'Nữ',
                'personalInfo': personal_info,
                'destinyInfo': destiny_info,
                'cungMenh': cung_menh,
                'cungThan': cung_than,
                'tenCungMenh': dia_ban_obj.thapNhiCung[cung_menh].cungTen,
                'tenCungThan': dia_ban_obj.thapNhiCung[cung_than].cungTen,
                'thienCan': can_chi_nam.split(" ")[0],
                'diaChi': can_chi_nam.split(" ")[1],
                'canChiNam': can_chi_nam,
                'lunarDate': lunar_date,
                'thapNhiCung': thap_nhi_cung,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing địa bàn: {str(e)}", exc_info=True)
            raise Exception(f"Lỗi khi phân tích dữ liệu: {str(e)}") from e

    @staticmethod
    def _get_attr(obj: Any, names: List[str], default: Any = None) -> Any:
        for name in names:
            if hasattr(obj, name):
                value = getattr(obj, name)
                if value is not None:
                    return value
        return default

    @staticmethod
    def _dia_chi_for_position(position: int) -> str:
        return LasoTuviService.DIA_CHI[(position - 1) % 12]

    @staticmethod
    def _get_can_chi_year(year: int) -> str:
        can = LasoTuviService.THIEN_CAN[(year - 4) % 10]
        chi = LasoTuviService.DIA_CHI[(year - 4) % 12]
        return f"{can} {chi}"

    @staticmethod
    def _get_nap_am(can_chi: str) -> Optional[str]:
        return LasoTuviService.NAP_AM_BY_CAN_CHI.get(can_chi)

    @staticmethod
    def _get_lunar_date(
        dia_ban_obj: Any,
        ngay: int,
        thang: int,
        nam: int,
        duong_lich: bool,
        time_zone: int,
    ) -> Optional[Dict[str, Any]]:
        engine_lunar = LasoTuviService._get_attr(
            dia_ban_obj,
            ['lunarDate', 'ngayAmLich', 'amLich', 'ngaySinhAmLich']
        )
        if isinstance(engine_lunar, dict):
            return engine_lunar

        lunar_day = LasoTuviService._get_attr(
            dia_ban_obj, ['lunarDay', 'ngayAm', 'ngayAmLich', 'ngaySinhAm', 'amLichNgay']
        )
        lunar_month = LasoTuviService._get_attr(
            dia_ban_obj, ['lunarMonth', 'thangAm', 'thangAmLich', 'thangSinhAm', 'amLichThang']
        )
        lunar_year = LasoTuviService._get_attr(
            dia_ban_obj, ['lunarYear', 'namAm', 'namAmLich', 'namSinhAm', 'amLichNam']
        )
        if lunar_day and lunar_month and lunar_year:
            return {
                'day': lunar_day,
                'month': lunar_month,
                'year': lunar_year,
                'leap_month': bool(LasoTuviService._get_attr(
                    dia_ban_obj, ['isLeapMonth', 'thangNhuan', 'leapMonth'], False
                )),
                'source': 'lasotuvi'
            }

        if not duong_lich:
            return {
                'day': ngay,
                'month': thang,
                'year': nam,
                'leap_month': False,
                'source': 'input'
            }

        try:
            import vnlunar  # type: ignore

            converters = ['solar_to_lunar', 'convertSolar2Lunar', 'Solar2Lunar']
            for converter_name in converters:
                converter = getattr(vnlunar, converter_name, None)
                if not converter:
                    continue
                try:
                    converted = converter(ngay, thang, nam, time_zone)
                except TypeError:
                    converted = converter(ngay, thang, nam)

                if isinstance(converted, dict):
                    return converted
                if isinstance(converted, (list, tuple)) and len(converted) >= 3:
                    return {
                        'day': converted[0],
                        'month': converted[1],
                        'year': converted[2],
                        'leap_month': bool(converted[3]) if len(converted) > 3 else False,
                        'source': 'vnlunar'
                    }
        except Exception:
            logger.debug("Unable to convert solar date to lunar date", exc_info=True)

        return LasoTuviService._convert_solar_to_lunar(ngay, thang, nam, time_zone)

    @staticmethod
    def _convert_solar_to_lunar(day: int, month: int, year: int, time_zone: int) -> Dict[str, Any]:
        day_number = LasoTuviService._jd_from_date(day, month, year)
        k = int((day_number - 2415021.076998695) / 29.530588853)
        month_start = LasoTuviService._get_new_moon_day(k + 1, time_zone)
        if month_start > day_number:
            month_start = LasoTuviService._get_new_moon_day(k, time_zone)

        a11 = LasoTuviService._get_lunar_month_11(year, time_zone)
        b11 = a11
        if a11 >= month_start:
            lunar_year = year
            a11 = LasoTuviService._get_lunar_month_11(year - 1, time_zone)
        else:
            lunar_year = year + 1
            b11 = LasoTuviService._get_lunar_month_11(year + 1, time_zone)

        lunar_day = day_number - month_start + 1
        diff = int((month_start - a11) / 29)
        lunar_leap = False
        lunar_month = diff + 11
        if b11 - a11 > 365:
            leap_month_diff = LasoTuviService._get_leap_month_offset(a11, time_zone)
            if diff >= leap_month_diff:
                lunar_month = diff + 10
                if diff == leap_month_diff:
                    lunar_leap = True
        if lunar_month > 12:
            lunar_month -= 12
        if lunar_month >= 11 and diff < 4:
            lunar_year -= 1

        return {
            'day': int(lunar_day),
            'month': int(lunar_month),
            'year': int(lunar_year),
            'leap_month': lunar_leap,
            'source': 'calculated'
        }

    @staticmethod
    def _jd_from_date(day: int, month: int, year: int) -> int:
        a = int((14 - month) / 12)
        y = year + 4800 - a
        m = month + 12 * a - 3
        jd = day + int((153 * m + 2) / 5) + 365 * y + int(y / 4) - int(y / 100) + int(y / 400) - 32045
        if jd < 2299161:
            jd = day + int((153 * m + 2) / 5) + 365 * y + int(y / 4) - 32083
        return jd

    @staticmethod
    def _get_new_moon_day(k: int, time_zone: int) -> int:
        t = k / 1236.85
        t2 = t * t
        t3 = t2 * t
        dr = math.pi / 180
        jd1 = (
            2415020.75933 + 29.53058868 * k + 0.0001178 * t2
            - 0.000000155 * t3
            + 0.00033 * math.sin((166.56 + 132.87 * t - 0.009173 * t2) * dr)
        )
        m = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3
        mpr = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3
        f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3
        c1 = (
            (0.1734 - 0.000393 * t) * math.sin(m * dr)
            + 0.0021 * math.sin(2 * dr * m)
            - 0.4068 * math.sin(mpr * dr)
            + 0.0161 * math.sin(2 * dr * mpr)
            - 0.0004 * math.sin(3 * dr * mpr)
            + 0.0104 * math.sin(2 * dr * f)
            - 0.0051 * math.sin((m + mpr) * dr)
            - 0.0074 * math.sin((m - mpr) * dr)
            + 0.0004 * math.sin((2 * f + m) * dr)
            - 0.0004 * math.sin((2 * f - m) * dr)
            - 0.0006 * math.sin((2 * f + mpr) * dr)
            + 0.0010 * math.sin((2 * f - mpr) * dr)
            + 0.0005 * math.sin((2 * mpr + m) * dr)
        )
        delta_t = 0.001 + 0.000839 * t + 0.0002261 * t2 - 0.00000845 * t3 - 0.000000081 * t * t3
        if t < -11:
            delta_t = (
                0.001
                + 0.000839 * t
                + 0.0002261 * t2
                - 0.00000845 * t3
                - 0.000000081 * t * t3
            )
        return int(jd1 + c1 - delta_t + 0.5 + time_zone / 24)

    @staticmethod
    def _get_sun_longitude(day_number: int, time_zone: int) -> int:
        t = (day_number - 2451545.5 - time_zone / 24) / 36525
        t2 = t * t
        dr = math.pi / 180
        m = 357.52910 + 35999.05030 * t - 0.0001559 * t2 - 0.00000048 * t * t2
        l0 = 280.46645 + 36000.76983 * t + 0.0003032 * t2
        dl = (
            (1.914600 - 0.004817 * t - 0.000014 * t2) * math.sin(dr * m)
            + (0.019993 - 0.000101 * t) * math.sin(2 * dr * m)
            + 0.000290 * math.sin(3 * dr * m)
        )
        l = (l0 + dl) * dr
        l = l - math.pi * 2 * int(l / (math.pi * 2))
        return int(l / math.pi * 6)

    @staticmethod
    def _get_lunar_month_11(year: int, time_zone: int) -> int:
        off = LasoTuviService._jd_from_date(31, 12, year) - 2415021
        k = int(off / 29.530588853)
        nm = LasoTuviService._get_new_moon_day(k, time_zone)
        sun_long = LasoTuviService._get_sun_longitude(nm, time_zone)
        if sun_long >= 9:
            nm = LasoTuviService._get_new_moon_day(k - 1, time_zone)
        return nm

    @staticmethod
    def _get_leap_month_offset(a11: int, time_zone: int) -> int:
        k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
        last = 0
        i = 1
        arc = LasoTuviService._get_sun_longitude(
            LasoTuviService._get_new_moon_day(k + i, time_zone), time_zone
        )
        while arc != last and i < 14:
            last = arc
            i += 1
            arc = LasoTuviService._get_sun_longitude(
                LasoTuviService._get_new_moon_day(k + i, time_zone), time_zone
            )
        return i - 1

    @staticmethod
    def _build_personal_info(
        dia_ban_obj: Any,
        ngay: int,
        thang: int,
        nam: int,
        gio: int,
        gioi_tinh: int,
        duong_lich: bool,
        time_zone: int,
        can_chi_nam: str,
        lunar_date: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        gio_chi = LasoTuviService.DIA_CHI[(gio - 1) % 12]
        can_nam = can_chi_nam.split(" ")[0]
        chi_nam = can_chi_nam.split(" ")[1]
        return {
            'solarDate': {
                'day': ngay,
                'month': thang,
                'year': nam,
                'is_input_calendar': duong_lich,
            },
            'lunarDate': lunar_date,
            'birthHour': {
                'index': gio,
                'dia_chi': gio_chi,
                'range': LasoTuviService.HOUR_RANGES.get(gio),
            },
            'gender': 'Nam' if gioi_tinh == 1 else 'Nữ',
            'amDuong': LasoTuviService._am_duong_gender(can_nam, gioi_tinh),
            'canChi': {
                'year': can_chi_nam,
                'month': LasoTuviService._get_attr(dia_ban_obj, ['canChiThang', 'thangCanChi']),
                'day': LasoTuviService._get_attr(dia_ban_obj, ['canChiNgay', 'ngayCanChi']),
                'hour': LasoTuviService._get_attr(dia_ban_obj, ['canChiGio', 'gioCanChi']),
            },
            'thienCan': can_nam,
            'diaChi': chi_nam,
            'timeZone': time_zone,
        }

    @staticmethod
    def _build_destiny_info(
        dia_ban_obj: Any,
        cung_menh: int,
        cung_than: int,
        can_chi_nam: str,
        nam: int,
        gio: int,
        lunar_date: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        menh_cung = dia_ban_obj.thapNhiCung[cung_menh]
        than_cung = dia_ban_obj.thapNhiCung[cung_than]
        return {
            'banMenh': LasoTuviService._get_attr(
                dia_ban_obj, ['banMenh', 'banMenhNapAm', 'menhNapAm'],
                LasoTuviService._get_nap_am(can_chi_nam)
            ),
            'cucMenh': LasoTuviService._get_attr(
                dia_ban_obj,
                ['cucMenh', 'menhCuc', 'cuc', 'tenCuc', 'cucSo', 'cucSoMenh'],
                LasoTuviService._infer_cuc_menh(menh_cung)
            ),
            'chuMenh': LasoTuviService._get_attr(
                dia_ban_obj,
                ['chuMenh', 'saoChuMenh', 'menhChu'],
                LasoTuviService._fallback_chu_menh(nam)
            ),
            'chuThan': LasoTuviService._get_attr(
                dia_ban_obj,
                ['chuThan', 'saoChuThan', 'thanChu'],
                LasoTuviService._fallback_chu_than(nam)
            ),
            'canLuong': LasoTuviService._get_attr(
                dia_ban_obj,
                ['canLuong', 'canLuongChiSo', 'canXuong', 'canXuongDoanSo'],
                LasoTuviService._calculate_can_luong(nam, lunar_date, gio)
            ),
            'laiNhanCung': LasoTuviService._get_attr(
                dia_ban_obj,
                ['laiNhanCung', 'cungLaiNhan', 'laiNhan'],
                LasoTuviService._format_cung_label(menh_cung)
            ),
            'thanCu': LasoTuviService._get_attr(
                dia_ban_obj,
                ['thanCu', 'thanCuCung', 'cungThanCu'],
                LasoTuviService._format_cung_label(than_cung)
            ),
            'cungMenh': cung_menh,
            'cungThan': cung_than,
        }

    @staticmethod
    def _format_cung_label(cung: Any) -> str:
        cung_chu = getattr(cung, 'cungChu', None)
        cung_ten = getattr(cung, 'cungTen', None)
        if cung_chu and cung_ten:
            return f"{cung_chu} ({cung_ten})"
        return str(cung_chu or cung_ten or "Chua ro")

    @staticmethod
    def _infer_cuc_menh(menh_cung: Any) -> str:
        element = LasoTuviService._normalize_text(getattr(menh_cung, 'hanhCung', ''))
        for key, label in LasoTuviService.CUC_BY_ELEMENT.items():
            if key in element:
                return label
        return "Chua ro cuc menh"

    @staticmethod
    def _fallback_chu_menh(year: int) -> str:
        branch_index = (year - 4) % 12
        return LasoTuviService.CHU_MENH_BY_BRANCH_INDEX[branch_index]

    @staticmethod
    def _fallback_chu_than(year: int) -> str:
        branch_index = (year - 4) % 12
        return LasoTuviService.CHU_THAN_BY_BRANCH_INDEX[branch_index]

    @staticmethod
    def _calculate_can_luong(
        year: int,
        lunar_date: Optional[Dict[str, Any]],
        gio: int,
    ) -> str:
        if not lunar_date:
            return "Chua du du lieu"

        try:
            lunar_month = int(lunar_date.get('month') or lunar_date.get('thang'))
            lunar_day = int(lunar_date.get('day') or lunar_date.get('ngay'))
        except (TypeError, ValueError, AttributeError):
            return "Chua du du lieu"

        if not 1 <= lunar_month <= 12 or not 1 <= lunar_day <= 30 or not 1 <= gio <= 12:
            return "Chua du du lieu"

        cycle_index = (year - 4) % 60
        total_chi = (
            LasoTuviService.CAN_LUONG_YEAR_WEIGHTS[cycle_index]
            + LasoTuviService.CAN_LUONG_MONTH_WEIGHTS[lunar_month - 1]
            + LasoTuviService.CAN_LUONG_DAY_WEIGHTS[lunar_day - 1]
            + LasoTuviService.CAN_LUONG_HOUR_WEIGHTS[gio - 1]
        )
        luong = total_chi // 10
        chi = total_chi % 10
        return f"{luong} luong {chi} chi"

    @staticmethod
    def _normalize_text(value: str) -> str:
        normalized = unicodedata.normalize("NFD", value).replace("đ", "d").replace("Đ", "D")
        without_marks = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
        return "".join(char.lower() if char.isalnum() else " " for char in without_marks).strip()

    @staticmethod
    def _am_duong_gender(can_nam: str, gioi_tinh: int) -> str:
        duong_can = {'Giáp', 'Bính', 'Mậu', 'Canh', 'Nhâm'}
        am_duong = 'Dương' if can_nam in duong_can else 'Âm'
        gender = 'Nam' if gioi_tinh == 1 else 'Nữ'
        return f"{am_duong} {gender}"

    @staticmethod
    def _get_trang_sinh(cung: Any, position: int) -> Optional[str]:
        engine_value = LasoTuviService._get_attr(
            cung, ['trangSinh', 'vongTrangSinh', 'cungTrangSinh']
        )
        if engine_value:
            return engine_value
        return LasoTuviService.TRANG_SINH[(position - 1) % 12]

    @staticmethod
    def _brightness_code(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        normalized = value.strip().lower()
        if 'hãm' in normalized or 'ham' in normalized:
            return 'H'
        if 'vượng' in normalized or 'vuong' in normalized:
            return 'V'
        if 'đắc' in normalized or 'dac' in normalized:
            return 'Đ'
        if 'miếu' in normalized or 'mieu' in normalized or 'mạnh' in normalized or 'manh' in normalized:
            return 'M'
        if 'bình' in normalized or 'binh' in normalized:
            return 'B'
        return value[:1].upper()

    @staticmethod
    def _brightness_color(value: Optional[str]) -> str:
        code = LasoTuviService._brightness_code(value)
        if code in {'M', 'V', 'Đ'}:
            return 'strong'
        if code == 'H':
            return 'weak'
        return 'neutral'

    @staticmethod
    def _star_category(name: Optional[str], star_id: Optional[int]) -> str:
        try:
            numeric_id = int(star_id) if star_id is not None else None
        except (TypeError, ValueError):
            numeric_id = None

        if numeric_id in LasoTuviService.CHINH_TINH_IDS:
            return 'Chính tinh'
        normalized = LasoTuviService._normalize_text(name or '')
        normalized_major_names = {
            LasoTuviService._normalize_text(star_name)
            for star_name in LasoTuviService.CHINH_TINH_NAMES
        }
        if normalized in normalized_major_names:
            return 'Chính tinh'
        return 'Phụ tinh'

    @staticmethod
    def _star_quality(name: Optional[str]) -> str:
        normalized = LasoTuviService._normalize_text(name or '')
        if normalized in LasoTuviService.SAT_TINH_NAMES:
            return 'sat_tinh'
        if normalized in LasoTuviService.CAT_TINH_NAMES:
            return 'cat_tinh'
        return 'cat_tinh'

    @staticmethod
    def get_cung_info(la_so_data: Dict[str, Any], cung_so: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific cung (palace)
        
        Args:
            la_so_data: Birth chart data from generate_la_so()
            cung_so: Cung number (1-12)
        
        Returns:
            Dictionary with cung information, or None if not found
        """
        if not 1 <= cung_so <= 12:
            return None
        
        for cung in la_so_data.get('thapNhiCung', []):
            if cung['cungSo'] == cung_so:
                return cung
        
        return None

    @staticmethod
    def get_sao_in_cung(la_so_data: Dict[str, Any], cung_so: int) -> List[Dict[str, Any]]:
        """
        Get all stars (sao) in a specific cung
        
        Args:
            la_so_data: Birth chart data
            cung_so: Cung number (1-12)
        
        Returns:
            List of sao dictionaries
        """
        cung_info = LasoTuviService.get_cung_info(la_so_data, cung_so)
        if cung_info:
            return cung_info.get('cungSao', [])
        return []

    @staticmethod
    def format_for_output(la_so_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format birth chart data for API response
        Adds human-readable summaries and interpretations
        
        Args:
            la_so_data: Raw birth chart data
        
        Returns:
            Formatted output suitable for API response
        """
        formatted = {
            'thongTinCanChi': {
                'ngay': la_so_data['ngay'],
                'thang': la_so_data['thang'],
                'nam': la_so_data['nam'],
                'gio': la_so_data['gio'],
                'gioiTinh': la_so_data['gioiTinh'],
                'duongLich': la_so_data.get('duongLich'),
                'personalInfo': la_so_data.get('personalInfo'),
                'destinyInfo': la_so_data.get('destinyInfo')
            },
            'daiCung': {
                'cungMenh': {
                    'index': la_so_data['cungMenh'],
                    'tenCung': la_so_data['tenCungMenh']
                },
                'cungThan': {
                    'index': la_so_data['cungThan'],
                    'tenCung': la_so_data['tenCungThan']
                }
            },
            'thapNhiCung': la_so_data['thapNhiCung'],
            'lunarDate': la_so_data.get('lunarDate'),
            'timestamp': la_so_data.get('timestamp')
        }
        
        return formatted
