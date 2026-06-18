"""
Chart calculation endpoints
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from app.models.chart import (
    TuViChartRequest,
    TuViChartResponse,
    ChartErrorResponse
)
from app.services.tuvi_calculator import (
    TuViCalculator,
    TuViCalculatorError,
    InvalidDateError,
    CalculationError
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chart", tags=["chart"])


@router.post(
    "/tuvi",
    response_model=TuViChartResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ChartErrorResponse, "description": "Invalid input"},
        500: {"model": ChartErrorResponse, "description": "Calculation error"}
    },
    summary="Calculate Tử Vi chart",
    description="Calculate a Tử Vi (Purple Star Astrology) chart based on birth date, time, and gender"
)
async def calculate_tuvi_chart(request: TuViChartRequest) -> TuViChartResponse:
    """
    Calculate Tử Vi chart.
    
    Args:
        request: Chart calculation request with birth info
        
    Returns:
        Complete Tử Vi chart with palaces and stars
        
    Raises:
        HTTPException: If validation or calculation fails
    """
    try:
        logger.info(f"Calculating Tử Vi chart for {request.birth_date} {request.birth_time}")
        
        # Initialize calculator
        calculator = TuViCalculator()
        
        # Calculate chart
        chart_data = calculator.calculate(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            gender=request.gender,
            label=request.label,
            nam_xem_han=request.nam_xem_han,
        )
        
        logger.info("Tử Vi chart calculated successfully")
        return TuViChartResponse(**chart_data)
        
    except InvalidDateError as e:
        logger.warning(f"Invalid date input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CalculationError as e:
        logger.error(f"Calculation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during chart calculation"
        )


@router.get(
    "/tuvi/test",
    summary="Test Tử Vi endpoint",
    description="Simple test endpoint to verify Tử Vi calculator is working"
)
async def test_tuvi():
    """Test endpoint for Tử Vi calculator"""
    try:
        calculator = TuViCalculator()
        return {
            "status": "ok",
            "message": "Tử Vi calculator is available",
            "calculator_type": type(calculator).__name__
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
