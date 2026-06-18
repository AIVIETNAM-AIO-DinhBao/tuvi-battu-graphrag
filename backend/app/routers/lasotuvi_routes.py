# -*- coding: utf-8 -*-
"""
FastAPI routes for Lasotuvi Tử Vi birth chart generation
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.models.lasotuvi_models import (
    GenerateLaSoRequest,
    LaSoTuViResponse,
    ErrorResponse,
    HealthResponse
)
from app.services.lasotuvi_service import LasoTuviService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/lasotuvi",
    tags=["lasotuvi"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check for Lasotuvi service",
    description="Check if the Lasotuvi engine is available and working"
)
async def health_check():
    """
    Health check endpoint for Lasotuvi service
    
    Returns:
        HealthResponse: Service health status
    """
    try:
        # Try importing lasotuvi to check availability
        from lasotuvi.DiaBan import diaBan
        from lasotuvi.App import lapDiaBan
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            lasotuvi_available=True
        )
    except ImportError as e:
        logger.warning(f"Lasotuvi not available: {str(e)}")
        return HealthResponse(
            status="degraded",
            version="1.0.0",
            lasotuvi_available=False
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="error",
            version="1.0.0",
            lasotuvi_available=False
        )


@router.post(
    "/generate",
    response_model=LaSoTuViResponse,
    summary="Generate Tử Vi birth chart",
    description="Generate a complete Tử Vi birth chart (lá số) from birth date/time information",
    responses={
        200: {
            "description": "Successfully generated birth chart",
            "content": {
                "application/json": {
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
                        "thapNhiCung": []
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Invalid input parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def generate_la_so(request: GenerateLaSoRequest):
    """
    Generate Tử Vi birth chart (lá số tử vi)
    
    Args:
        request: Birth date/time information including:
            - ngay: Day of birth (1-31)
            - thang: Month of birth (1-12)
            - nam: Year of birth (1900-2100)
            - gio: Hour of birth (1-12, where 1=Tý, 12=Hợi)
            - gioi_tinh: Gender (1=Nam/Male, -1=Nữ/Female)
            - duong_lich: True for Gregorian calendar, False for Lunar
            - time_zone: Timezone offset (default 7 for Vietnam)
    
    Returns:
        LaSoTuViResponse: Complete birth chart with 12 cung (palaces) and stars
    
    Raises:
        HTTPException: 400 for invalid input, 500 for server errors
    """
    try:
        logger.info(f"Generating lá số for {request.ngay}/{request.thang}/{request.nam}")
        
        # Generate birth chart using service
        la_so_data = LasoTuviService.generate_la_so(
            ngay=request.ngay,
            thang=request.thang,
            nam=request.nam,
            gio=request.gio,
            gioi_tinh=request.gioi_tinh,
            duong_lich=request.duong_lich,
            time_zone=request.time_zone,
            nam_xem_han=request.nam_xem_han,
        )
        
        # Format for output
        formatted_data = LasoTuviService.format_for_output(la_so_data)
        
        return LaSoTuViResponse(**formatted_data)
        
    except ValueError as ve:
        logger.warning(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error generating lá số: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi sinh lá số: {str(e)}"
        )


@router.get(
    "/generate",
    response_model=LaSoTuViResponse,
    summary="Generate Tử Vi birth chart (GET method)",
    description="Generate birth chart using query parameters (alternative to POST)"
)
async def generate_la_so_get(
    ngay: int,
    thang: int,
    nam: int,
    gio: int,
    gioi_tinh: int,
    duong_lich: bool = True,
    time_zone: int = 7,
    nam_xem_han: int | None = None,
):
    """
    Generate Tử Vi birth chart using GET method
    
    This is a convenience endpoint for testing and simple integrations.
    For production use, prefer the POST endpoint.
    
    Query parameters:
        ngay: Day of birth (1-31)
        thang: Month of birth (1-12)
        nam: Year of birth (1900-2100)
        gio: Hour of birth (1-12)
        gioi_tinh: Gender (1=Nam, -1=Nữ)
        duong_lich: True for Gregorian calendar
        time_zone: Timezone offset (default 7)
    """
    try:
        la_so_data = LasoTuviService.generate_la_so(
            ngay=ngay,
            thang=thang,
            nam=nam,
            gio=gio,
            gioi_tinh=gioi_tinh,
            duong_lich=duong_lich,
            time_zone=time_zone,
            nam_xem_han=nam_xem_han,
        )
        
        formatted_data = LasoTuviService.format_for_output(la_so_data)
        return LaSoTuViResponse(**formatted_data)
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error generating lá số: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi sinh lá số: {str(e)}"
        )
