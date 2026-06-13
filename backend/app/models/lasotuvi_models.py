# -*- coding: utf-8 -*-
"""
Pydantic models for Lasotuvi Tử Vi birth chart data
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class SaoInfo(BaseModel):
    """Information about a star (sao) in Tử Vi"""
    saoTen: str = Field(..., description="Tên sao")
    saoDacTinh: Optional[str] = Field(None, description="Đặc tính của sao (Mãnh, Vượng, Đắc, Bình, Hãm)")
    saoID: Optional[int] = Field(None, description="ID của sao")

    class Config:
        schema_extra = {
            "example": {
                "saoTen": "Tử vi",
                "saoDacTinh": "Vượng",
                "saoID": 1
            }
        }


class CungInfo(BaseModel):
    """Information about a cung (palace) in Tử Vi"""
    cungSo: int = Field(..., ge=1, le=12, description="Số thứ tự cung (1-12)")
    cungTen: str = Field(..., description="Tên cung (Tý, Sửu, Dần, ...)")
    cungChu: str = Field(..., description="Cung chủ (Mệnh, Phụ mẫu, Phúc đức, ...)")
    hanhCung: str = Field(..., description="Hành của cung (Kim, Mộc, Thủy, Hỏa, Thổ)")
    amDuong: str = Field(..., description="Âm dương của cung (Âm hoặc Dương)")
    daiHan: Optional[int] = Field(None, description="Đại hạn (tuổi)")
    tieuHan: Optional[str] = Field(None, description="Tiểu hạn (cung)")
    coThhan: bool = Field(..., description="Có cung Thân ký cư hay không")
    cungSao: List[SaoInfo] = Field(..., description="Danh sách sao trong cung")

    class Config:
        schema_extra = {
            "example": {
                "cungSo": 5,
                "cungTen": "Thìn",
                "cungChu": "Quan lộc",
                "hanhCung": "Thổ",
                "amDuong": "Dương",
                "daiHan": 32,
                "tieuHan": "Tý",
                "coThhan": False,
                "cungSao": [
                    {"saoTen": "Thái dương", "saoDacTinh": "Mãnh", "saoID": 5},
                    {"saoTen": "Văn xương", "saoDacTinh": "Đắc", "saoID": 57}
                ]
            }
        }


class LaSoTuViResponse(BaseModel):
    """Complete Tử Vi birth chart response"""
    thongTinCanChi: Dict[str, Any] = Field(..., description="Thông tin Can Chi")
    daiCung: Dict[str, Any] = Field(..., description="Thông tin đại cung (Mệnh, Thân)")
    thapNhiCung: List[CungInfo] = Field(..., description="Thông tin 12 cung")
    timestamp: Optional[str] = Field(None, description="Thời điểm sinh lá số")

    class Config:
        schema_extra = {
            "example": {
                "thongTinCanChi": {
                    "ngay": 15,
                    "thang": 10,
                    "nam": 1990,
                    "gio": 6,
                    "gioiTinh": "Nam"
                },
                "daiCung": {
                    "cungMenh": {"index": 5, "tenCung": "Thìn"},
                    "cungThan": {"index": 11, "tenCung": "Tuất"}
                },
                "thapNhiCung": [
                    {
                        "cungSo": 1,
                        "cungTen": "Tý",
                        "cungChu": "Mệnh",
                        "hanhCung": "Thủy",
                        "amDuong": "Dương",
                        "daiHan": 22,
                        "tieuHan": "Dần",
                        "coThhan": False,
                        "cungSao": [
                            {"saoTen": "Tử vi", "saoDacTinh": "Mãnh", "saoID": 1}
                        ]
                    }
                ],
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class GenerateLaSoRequest(BaseModel):
    """Request body for generating Tử Vi birth chart"""
    ngay: int = Field(..., ge=1, le=31, description="Ngày sinh (1-31)")
    thang: int = Field(..., ge=1, le=12, description="Tháng sinh (1-12)")
    nam: int = Field(..., ge=1900, le=2100, description="Năm sinh (1900-2100)")
    gio: int = Field(..., ge=1, le=12, description="Giờ sinh (1=Tý, 12=Hợi)")
    gioi_tinh: int = Field(..., description="Giới tính (1=Nam, -1=Nữ)")
    duong_lich: bool = Field(True, description="True nếu là lịch Dương, False nếu là Âm lịch")
    time_zone: int = Field(7, description="Múi giờ (mặc định 7 cho Việt Nam)")

    @validator('gio')
    def validate_gio(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Giờ sinh phải từ 1-12 (1=Tý, 12=Hợi)')
        return v

    @validator('gioi_tinh')
    def validate_gioi_tinh(cls, v):
        if v not in [1, -1]:
            raise ValueError('Giới tính phải là 1 (Nam) hoặc -1 (Nữ)')
        return v

    @validator('nam')
    def validate_nam(cls, v):
        if v < 1900 or v > 2100:
            raise ValueError('Năm sinh phải từ 1900-2100')
        return v

    @property
    def gioi_tinh_text(self) -> str:
        """Return gender as text"""
        return "Nam" if self.gioi_tinh == 1 else "Nữ"

    @property
    def gio_text(self) -> str:
        """Return hour as text"""
        gio_mapping = {
            1: "Tý", 2: "Sửu", 3: "Dần", 4: "Mão",
            5: "Thìn", 6: "Tỵ", 7: "Ngọ", 8: "Mùi",
            9: "Thân", 10: "Dậu", 11: "Tuất", 12: "Hợi"
        }
        return gio_mapping.get(self.gio, f"Giờ {self.gio}")

    class Config:
        schema_extra = {
            "example": {
                "ngay": 15,
                "thang": 10,
                "nam": 1990,
                "gio": 6,
                "gioi_tinh": 1,
                "duong_lich": True,
                "time_zone": 7
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        schema_extra = {
            "example": {
                "error": "Ngày sinh không hợp lệ",
                "details": "Ngày sinh phải trong khoảng 1-31"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    lasotuvi_available: bool = Field(..., description="Whether lasotuvi engine is available")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "lasotuvi_available": True
            }
        }