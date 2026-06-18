# -*- coding: utf-8 -*-
"""
Pydantic models for Lasotuvi Tu Vi birth chart data.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class SaoInfo(BaseModel):
    """Information about a star (sao) in Tu Vi."""

    saoTen: str = Field(..., description="Star name")
    saoDacTinh: Optional[str] = Field(None, description="Star brightness/state")
    saoDacTinhCode: Optional[str] = Field(None, description="Brightness code: M, V, D, B, H")
    saoNhom: Optional[str] = Field(None, description="Star group/category")
    saoTinhChat: Optional[str] = Field(None, description="Star quality: cat_tinh or sat_tinh")
    saoColor: Optional[str] = Field(None, description="Display color hint")
    saoID: Optional[int] = Field(None, description="Star ID")
    isLuu: Optional[bool] = Field(False, description="Whether this is an annual transit star")
    is_luu: Optional[bool] = Field(False, description="Snake-case alias for annual transit stars")
    source: Optional[str] = Field(None, description="Star placement source")
    namXemHan: Optional[int] = Field(None, description="Annual transit year")
    nam_xem_han: Optional[int] = Field(None, description="Snake-case annual transit year")

    class Config:
        schema_extra = {
            "example": {
                "saoTen": "Tu vi",
                "saoDacTinh": "Vuong",
                "saoDacTinhCode": "V",
                "saoNhom": "Chinh tinh",
                "saoTinhChat": "cat_tinh",
                "saoColor": "strong",
                "saoID": 1,
            }
        }


class CungInfo(BaseModel):
    """Information about a cung (palace) in Tu Vi."""

    cungSo: int = Field(..., ge=1, le=12, description="Palace number, 1-12")
    cungTen: str = Field(..., description="Palace earthly-branch name")
    diaChi: Optional[str] = Field(None, description="Earthly branch")
    cungChu: str = Field(..., description="Palace role/name")
    hanhCung: str = Field(..., description="Palace element")
    amDuong: str = Field(..., description="Yin/yang of the palace")
    daiHan: Optional[int] = Field(None, description="Major cycle age")
    tuoiDaiHan: Optional[int] = Field(None, description="Displayed major cycle age")
    tieuHan: Optional[str] = Field(None, description="Minor cycle marker")
    luuNienDaiVan: Optional[Any] = Field(None, description="Annual major-cycle marker")
    trangSinh: Optional[str] = Field(None, description="Trang sinh cycle state")
    coThan: Optional[bool] = Field(None, description="Whether Than resides in this palace")
    coThhan: bool = Field(..., description="Backward-compatible typo alias for coThan")
    tuanKhong: Optional[bool] = Field(False, description="Whether Tuan Khong affects this palace")
    trietKhong: Optional[bool] = Field(False, description="Whether Triet Khong affects this palace")
    khongVong: List[str] = Field(default_factory=list, description="Void markers affecting this palace")
    cungSao: List[SaoInfo] = Field(..., description="Stars in this palace")

    class Config:
        schema_extra = {
            "example": {
                "cungSo": 5,
                "cungTen": "Thin",
                "diaChi": "Thin",
                "cungChu": "Quan loc",
                "hanhCung": "Tho",
                "amDuong": "Duong",
                "daiHan": 32,
                "tuoiDaiHan": 32,
                "tieuHan": "Ty",
                "trangSinh": "De vuong",
                "coThan": False,
                "coThhan": False,
                "cungSao": [
                    {
                        "saoTen": "Thai duong",
                        "saoDacTinh": "Mieu",
                        "saoDacTinhCode": "M",
                        "saoNhom": "Chinh tinh",
                        "saoColor": "strong",
                        "saoID": 5,
                    }
                ],
            }
        }


class LaSoTuViResponse(BaseModel):
    """Complete Tu Vi birth chart response."""

    thongTinCanChi: Dict[str, Any] = Field(..., description="Personal and can-chi information")
    daiCung: Dict[str, Any] = Field(..., description="Menh and Than palace information")
    thapNhiCung: List[CungInfo] = Field(..., description="The 12 palaces")
    lunarDate: Optional[Dict[str, Any]] = Field(None, description="Lunar calendar date")
    timestamp: Optional[str] = Field(None, description="Generation timestamp")

    class Config:
        schema_extra = {
            "example": {
                "thongTinCanChi": {
                    "ngay": 15,
                    "thang": 10,
                    "nam": 1990,
                    "gio": 6,
                    "gioiTinh": "Nam",
                },
                "daiCung": {
                    "cungMenh": {"index": 5, "tenCung": "Thin"},
                    "cungThan": {"index": 11, "tenCung": "Tuat"},
                },
                "thapNhiCung": [],
                "timestamp": "2026-06-17T10:30:00",
            }
        }


class GenerateLaSoRequest(BaseModel):
    """Request body for generating Tu Vi birth chart."""

    ngay: int = Field(..., ge=1, le=31, description="Birth day, 1-31")
    thang: int = Field(..., ge=1, le=12, description="Birth month, 1-12")
    nam: int = Field(..., ge=1900, le=2100, description="Birth year, 1900-2100")
    gio: int = Field(..., ge=1, le=12, description="Birth hour branch, 1=Ty, 12=Hoi")
    gioi_tinh: int = Field(..., description="Gender: 1=male, -1=female")
    duong_lich: bool = Field(True, description="True for Gregorian input, false for lunar input")
    time_zone: int = Field(7, description="UTC offset")
    nam_xem_han: Optional[int] = Field(
        None,
        ge=1900,
        le=2100,
        description="Annual transit year. Defaults to the current Vietnam year."
    )

    @validator('gio')
    def validate_gio(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Gio sinh phai tu 1-12')
        return v

    @validator('gioi_tinh')
    def validate_gioi_tinh(cls, v):
        if v not in [1, -1]:
            raise ValueError('Gioi tinh phai la 1 hoac -1')
        return v

    @validator('nam')
    def validate_nam(cls, v):
        if v < 1900 or v > 2100:
            raise ValueError('Nam sinh phai tu 1900-2100')
        return v

    @property
    def gioi_tinh_text(self) -> str:
        return "Nam" if self.gioi_tinh == 1 else "Nu"

    @property
    def gio_text(self) -> str:
        gio_mapping = {
            1: "Ty", 2: "Suu", 3: "Dan", 4: "Mao",
            5: "Thin", 6: "Ty.", 7: "Ngo", 8: "Mui",
            9: "Than", 10: "Dau", 11: "Tuat", 12: "Hoi",
        }
        return gio_mapping.get(self.gio, f"Gio {self.gio}")

    class Config:
        schema_extra = {
            "example": {
                "ngay": 15,
                "thang": 10,
                "nam": 1990,
                "gio": 6,
                "gioi_tinh": 1,
                "duong_lich": True,
                "time_zone": 7,
                "nam_xem_han": 2026,
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    lasotuvi_available: bool = Field(..., description="Whether lasotuvi engine is available")
