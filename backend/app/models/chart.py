"""
Pydantic models for chart requests and responses
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TuViChartRequest(BaseModel):
    """Request model for Tử Vi chart calculation"""
    birth_date: str = Field(
        ...,
        description="Birth date in ISO format (YYYY-MM-DD)",
        examples=["1990-01-15"]
    )
    birth_time: str = Field(
        ...,
        description="Birth time in HH:MM or HH:MM:SS format",
        examples=["14:30", "14:30:00"]
    )
    gender: str = Field(
        ...,
        description="Gender: 'male' or 'female'",
        examples=["male", "female"]
    )
    label: Optional[str] = Field(
        None,
        description="Optional label for this chart",
        examples=["Lá số của tôi"]
    )
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Validate gender field"""
        if v.lower() not in ('male', 'female', 'nam', 'nữ', 'nu'):
            raise ValueError("Gender must be 'male' or 'female'")
        return v
    
    @field_validator('birth_date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format"""
        try:
            datetime.fromisoformat(v)
        except (ValueError, AttributeError):
            raise ValueError("Birth date must be in YYYY-MM-DD format")
        return v


class PalaceInfo(BaseModel):
    """Information about a palace (cung)"""
    name: str
    stars: List[str] = Field(default_factory=list)
    star_details: List[Dict[str, Any]] = Field(default_factory=list)
    star_groups: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    position: Optional[int] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class StarInfo(BaseModel):
    """Information about a star (sao)"""
    name: str
    palace: Optional[str] = None
    brightness: Optional[str] = None
    category: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class TuViChartResponse(BaseModel):
    """Response model for Tử Vi chart"""
    chart_type: str = "TUVI"
    version: str = "1.0"
    metadata: Dict[str, Any]
    palaces: Dict[str, PalaceInfo]
    stars: Dict[str, StarInfo]
    thien_can: Optional[str] = None
    dia_chi: Optional[str] = None
    lunar_date: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_type": "TUVI",
                "version": "1.0",
                "metadata": {
                    "label": "Lá số Tử Vi",
                    "birth_date": "1990-01-15",
                    "birth_time": "14:30",
                    "gender": "male",
                    "calculated_at": "2026-06-11T13:30:00Z"
                },
                "palaces": {
                    "Mệnh": {
                        "name": "Mệnh",
                        "stars": ["Tử Vi", "Thiên Phủ"],
                        "position": 1,
                        "attributes": {}
                    }
                },
                "stars": {
                    "Tử Vi": {
                        "name": "Tử Vi",
                        "palace": "Mệnh",
                        "brightness": "Miếu",
                        "category": "Chính Tinh",
                        "attributes": {}
                    }
                }
            }
        }


class ChartErrorResponse(BaseModel):
    """Error response for chart calculation"""
    error: str
    detail: Optional[str] = None
    error_type: str = "CalculationError"
