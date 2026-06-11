"""
Tử Vi Calculator Service
Wrapper around lasotuvi engine with normalized output schema.
"""
from typing import Dict, Any, Optional
from datetime import datetime, date, time
import logging

try:
    from lasotuvi import LasoTuVi
except ImportError:
    LasoTuVi = None
    logging.warning("lasotuvi package not available")

logger = logging.getLogger(__name__)


class TuViCalculatorError(Exception):
    """Base exception for TuVi calculator errors"""
    pass


class InvalidDateError(TuViCalculatorError):
    """Raised when birth date/time is invalid"""
    pass


class CalculationError(TuViCalculatorError):
    """Raised when calculation fails"""
    pass


class TuViCalculator:
    """
    Tử Vi Calculator service using lasotuvi engine.
    Provides normalized, consistent output schema.
    """
    
    def __init__(self):
        if LasoTuVi is None:
            raise RuntimeError("lasotuvi package not installed")
    
    def calculate(
        self,
        birth_date: str,
        birth_time: str,
        gender: str,
        label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate Tử Vi chart.
        
        Args:
            birth_date: ISO date string (YYYY-MM-DD)
            birth_time: Time string (HH:MM or HH:MM:SS)
            gender: "male" or "female"
            label: Optional label for the chart
            
        Returns:
            Normalized Tử Vi chart dictionary
            
        Raises:
            InvalidDateError: If date/time is invalid
            CalculationError: If calculation fails
        """
        try:
            # Parse and validate inputs
            parsed_date = self._parse_date(birth_date)
            parsed_time = self._parse_time(birth_time)
            normalized_gender = self._normalize_gender(gender)
            
            # Calculate using lasotuvi
            year = parsed_date.year
            month = parsed_date.month
            day = parsed_date.day
            hour = parsed_time.hour
            
            logger.info(f"Calculating Tử Vi for {year}-{month}-{day} {hour}h, gender={normalized_gender}")
            
            # Create LasoTuVi instance
            laso = LasoTuVi(year, month, day, hour, normalized_gender)
            
            # Get raw output
            raw_chart = self._extract_chart_data(laso)
            
            # Normalize to internal schema
            normalized = self._normalize_output(
                raw_chart=raw_chart,
                birth_date=birth_date,
                birth_time=birth_time,
                gender=gender,
                label=label
            )
            
            return normalized
            
        except (ValueError, TypeError) as e:
            raise InvalidDateError(f"Invalid input: {str(e)}")
        except Exception as e:
            logger.error(f"Calculation failed: {str(e)}", exc_info=True)
            raise CalculationError(f"Failed to calculate chart: {str(e)}")
    
    def _parse_date(self, date_str: str) -> date:
        """Parse ISO date string"""
        try:
            return datetime.fromisoformat(date_str).date()
        except (ValueError, AttributeError):
            raise InvalidDateError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    def _parse_time(self, time_str: str) -> time:
        """Parse time string (HH:MM or HH:MM:SS)"""
        try:
            # Try HH:MM:SS format first
            if len(time_str.split(':')) == 3:
                return datetime.strptime(time_str, "%H:%M:%S").time()
            else:
                return datetime.strptime(time_str, "%H:%M").time()
        except (ValueError, AttributeError):
            raise InvalidDateError(f"Invalid time format: {time_str}. Expected HH:MM or HH:MM:SS")
    
    def _normalize_gender(self, gender: str) -> int:
        """Convert gender to lasotuvi format (0=male, 1=female)"""
        gender_lower = gender.lower().strip()
        if gender_lower in ("male", "nam", "0"):
            return 0
        elif gender_lower in ("female", "nữ", "nu", "1"):
            return 1
        else:
            raise InvalidDateError(f"Invalid gender: {gender}. Expected 'male' or 'female'")
    
    def _extract_chart_data(self, laso: Any) -> Dict[str, Any]:
        """Extract chart data from LasoTuVi instance"""
        # This method extracts raw data from lasotuvi
        # The exact structure depends on the lasotuvi package API
        # We'll build a comprehensive structure here
        
        chart_data = {
            "cung_data": {},
            "sao_data": {},
            "thien_can": None,
            "dia_chi": None,
            "lunar_date": None,
            "metadata": {}
        }
        
        try:
            # Extract palace (cung) data
            # Assuming lasotuvi has methods to get palace info
            if hasattr(laso, 'get_palaces') or hasattr(laso, 'cung'):
                chart_data["cung_data"] = self._extract_palaces(laso)
            
            # Extract star (sao) data
            if hasattr(laso, 'get_stars') or hasattr(laso, 'sao'):
                chart_data["sao_data"] = self._extract_stars(laso)
            
            # Extract Can Chi data
            if hasattr(laso, 'thien_can'):
                chart_data["thien_can"] = laso.thien_can
            if hasattr(laso, 'dia_chi'):
                chart_data["dia_chi"] = laso.dia_chi
            
            # Extract lunar date if available
            if hasattr(laso, 'lunar_date'):
                chart_data["lunar_date"] = laso.lunar_date
                
        except Exception as e:
            logger.warning(f"Failed to extract some chart data: {str(e)}")
        
        return chart_data
    
    def _extract_palaces(self, laso: Any) -> Dict[str, Any]:
        """Extract palace (cung) information"""
        palaces = {}
        
        # Standard 12 palaces in Tử Vi
        palace_names = [
            "Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch",
            "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách",
            "Tài Bạch", "Tử Nữ", "Phu Thê", "Huynh Đệ"
        ]
        
        for palace_name in palace_names:
            try:
                # Try different possible API patterns
                if hasattr(laso, 'get_palace'):
                    palace_data = laso.get_palace(palace_name)
                elif hasattr(laso, 'cung') and isinstance(laso.cung, dict):
                    palace_data = laso.cung.get(palace_name, {})
                else:
                    palace_data = {}
                
                palaces[palace_name] = palace_data
            except Exception as e:
                logger.debug(f"Could not extract {palace_name}: {e}")
                palaces[palace_name] = {}
        
        return palaces
    
    def _extract_stars(self, laso: Any) -> Dict[str, Any]:
        """Extract star (sao) information"""
        stars = {}
        
        try:
            # Try different API patterns
            if hasattr(laso, 'get_all_stars'):
                stars = laso.get_all_stars()
            elif hasattr(laso, 'sao') and isinstance(laso.sao, dict):
                stars = laso.sao
            elif hasattr(laso, 'stars'):
                stars = laso.stars
        except Exception as e:
            logger.debug(f"Could not extract stars: {e}")
        
        return stars
    
    def _normalize_output(
        self,
        raw_chart: Dict[str, Any],
        birth_date: str,
        birth_time: str,
        gender: str,
        label: Optional[str]
    ) -> Dict[str, Any]:
        """
        Normalize raw chart output to internal schema.
        
        This creates a consistent structure regardless of lasotuvi API changes.
        """
        return {
            "chart_type": "TUVI",
            "version": "1.0",
            "metadata": {
                "label": label or "Lá số Tử Vi",
                "birth_date": birth_date,
                "birth_time": birth_time,
                "gender": gender,
                "calculated_at": datetime.utcnow().isoformat() + "Z"
            },
            "palaces": self._normalize_palaces(raw_chart.get("cung_data", {})),
            "stars": self._normalize_stars(raw_chart.get("sao_data", {})),
            "thien_can": raw_chart.get("thien_can"),
            "dia_chi": raw_chart.get("dia_chi"),
            "lunar_date": raw_chart.get("lunar_date"),
            "raw_data": raw_chart  # Keep raw data for debugging
        }
    
    def _normalize_palaces(self, cung_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize palace data to consistent structure"""
        normalized = {}
        
        for palace_name, palace_info in cung_data.items():
            normalized[palace_name] = {
                "name": palace_name,
                "stars": palace_info.get("stars", []) if isinstance(palace_info, dict) else [],
                "position": palace_info.get("position") if isinstance(palace_info, dict) else None,
                "attributes": palace_info.get("attributes", {}) if isinstance(palace_info, dict) else {}
            }
        
        return normalized
    
    def _normalize_stars(self, sao_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize star data to consistent structure"""
        normalized = {}
        
        for star_name, star_info in sao_data.items():
            if isinstance(star_info, dict):
                normalized[star_name] = {
                    "name": star_name,
                    "palace": star_info.get("palace", star_info.get("cung")),
                    "brightness": star_info.get("brightness", star_info.get("trang_thai")),
                    "category": star_info.get("category", star_info.get("loai")),
                    "attributes": star_info.get("attributes", {})
                }
            else:
                # If star_info is just a string (palace name), create simple structure
                normalized[star_name] = {
                    "name": star_name,
                    "palace": str(star_info) if star_info else None,
                    "brightness": None,
                    "category": None,
                    "attributes": {}
                }
        
        return normalized