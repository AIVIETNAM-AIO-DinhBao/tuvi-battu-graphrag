# -*- coding: utf-8 -*-
"""
Lasotuvi Service - Wrapper around lasotuvi engine for Tử Vi calculations
Provides structured interface for generating Tử Vi lá số (birth chart)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LasoTuviService:
    """Service for generating Tử Vi birth charts using lasotuvi engine"""

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
            result = LasoTuviService._parse_dia_ban(dia_ban_obj, ngay, thang, nam, gio, gioi_tinh)
            
            logger.info("✓ Successfully generated lá số")
            return result
            
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error generating lá số: {str(e)}", exc_info=True)
            raise Exception(f"Lỗi khi sinh lá số: {str(e)}") from e

    @staticmethod
    def _parse_dia_ban(dia_ban_obj: Any, ngay: int, thang: int, nam: int, gio: int, gioi_tinh: int) -> Dict[str, Any]:
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
            
            # Process 12 cung (palaces)
            thap_nhi_cung = []
            for i in range(1, 13):  # Start from 1, skip index 0
                cung = dia_ban_obj.thapNhiCung[i]
                
                # Extract sao (stars) in this cung
                danh_sach_sao = []
                if hasattr(cung, 'cungSao') and cung.cungSao:
                    for sao in cung.cungSao:
                        sao_info = {
                            'saoTen': sao.get('saoTen', 'Không rõ tên'),
                            'saoDacTinh': sao.get('saoDacTinh'),
                            'saoID': sao.get('saoID')
                        }
                        danh_sach_sao.append(sao_info)
                
                # Get cung properties
                cung_chu = getattr(cung, 'cungChu', 'N/A')
                dai_han = getattr(cung, 'cungDaiHan', None)
                tieu_han = getattr(cung, 'cungTieuHan', None)
                am_duong = 'Dương' if cung.cungAmDuong == 1 else 'Âm'
                
                cung_data = {
                    'cungSo': cung.cungSo,
                    'cungTen': cung.cungTen,
                    'cungChu': cung_chu,
                    'hanhCung': cung.hanhCung,
                    'amDuong': am_duong,
                    'daiHan': dai_han,
                    'tieuHan': tieu_han,
                    'coThhan': getattr(cung, 'cungThan', False),
                    'cungSao': danh_sach_sao
                }
                
                thap_nhi_cung.append(cung_data)
            
            # Build final result
            result = {
                'ngay': ngay,
                'thang': thang,
                'nam': nam,
                'gio': gio,
                'gioiTinh': 'Nam' if gioi_tinh == 1 else 'Nữ',
                'cungMenh': cung_menh,
                'cungThan': cung_than,
                'tenCungMenh': dia_ban_obj.thapNhiCung[cung_menh].cungTen,
                'tenCungThan': dia_ban_obj.thapNhiCung[cung_than].cungTen,
                'thapNhiCung': thap_nhi_cung,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing địa bàn: {str(e)}", exc_info=True)
            raise Exception(f"Lỗi khi phân tích dữ liệu: {str(e)}") from e

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
                'gioiTinh': la_so_data['gioiTinh']
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
            'thapNhiCung': la_so_data['thapNhiCung']
        }
        
        return formatted