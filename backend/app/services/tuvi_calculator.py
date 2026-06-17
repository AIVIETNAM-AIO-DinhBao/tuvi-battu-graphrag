"""
Tu Vi Calculator Service

Normalizes the low-level doanguyen/lasotuvi output into the internal
chart schema used by /chart/tuvi and frontend storage.
"""
from typing import Any, Dict, Optional
from datetime import datetime, date, time, timezone
import logging

from app.services.lasotuvi_service import LasoTuviService

logger = logging.getLogger(__name__)


class TuViCalculatorError(Exception):
    """Base exception for Tu Vi calculator errors."""


class InvalidDateError(TuViCalculatorError):
    """Raised when birth date/time is invalid."""


class CalculationError(TuViCalculatorError):
    """Raised when calculation fails."""


class TuViCalculator:
    """Tu Vi calculator wrapper with a stable normalized output schema."""

    PALACE_NAME_MAP = {
        "mệnh": "Mệnh",
        "phụ mẫu": "Phụ Mẫu",
        "phúc đức": "Phúc Đức",
        "điền trạch": "Điền Trạch",
        "quan lộc": "Quan Lộc",
        "nô bộc": "Nô Bộc",
        "thiên di": "Thiên Di",
        "tật ách": "Tật Ách",
        "tài bạch": "Tài Bạch",
        "tử nữ": "Tử Nữ",
        "tử tức": "Tử Nữ",
        "phu thê": "Phu Thê",
        "huynh đệ": "Huynh Đệ",
    }

    MAJOR_STARS = {
        "Tử vi",
        "Thiên cơ",
        "Thái dương",
        "Vũ khúc",
        "Thiên đồng",
        "Liêm trinh",
        "Thiên phủ",
        "Thái âm",
        "Tham lang",
        "Cự môn",
        "Thiên tướng",
        "Thiên lương",
        "Thất sát",
        "Phá quân",
    }

    def calculate(
        self,
        birth_date: str,
        birth_time: str,
        gender: str,
        label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate a Tu Vi chart from ISO date, clock time, and gender.

        Args:
            birth_date: ISO date string (YYYY-MM-DD)
            birth_time: Time string (HH:MM or HH:MM:SS)
            gender: male/female, nam/nu, or 0/1
            label: Optional chart label
        """
        try:
            parsed_date = self._parse_date(birth_date)
            parsed_time = self._parse_time(birth_time)
            normalized_gender = self._normalize_gender(gender)

            lasotuvi_hour = self._to_lasotuvi_hour(parsed_time.hour)
            logger.info(
                "Calculating Tu Vi for %s %s, lasotuvi_hour=%s, gender=%s",
                birth_date,
                birth_time,
                lasotuvi_hour,
                normalized_gender,
            )

            raw_chart = LasoTuviService.generate_la_so(
                ngay=parsed_date.day,
                thang=parsed_date.month,
                nam=parsed_date.year,
                gio=lasotuvi_hour,
                gioi_tinh=normalized_gender,
            )

            return self._normalize_output(
                raw_chart=raw_chart,
                birth_date=birth_date,
                birth_time=birth_time,
                gender=gender,
                label=label,
            )

        except InvalidDateError:
            raise
        except ValueError as exc:
            raise InvalidDateError(f"Invalid input: {exc}") from exc
        except Exception as exc:
            logger.error("Calculation failed: %s", exc, exc_info=True)
            raise CalculationError(f"Failed to calculate chart: {exc}") from exc

    def _parse_date(self, date_str: str) -> date:
        """Parse ISO date string."""
        try:
            return datetime.fromisoformat(date_str).date()
        except (ValueError, AttributeError) as exc:
            raise InvalidDateError(
                f"Invalid date format: {date_str}. Expected YYYY-MM-DD"
            ) from exc

    def _parse_time(self, time_str: str) -> time:
        """Parse time string in HH:MM or HH:MM:SS format."""
        try:
            if len(time_str.split(":")) == 3:
                return datetime.strptime(time_str, "%H:%M:%S").time()
            return datetime.strptime(time_str, "%H:%M").time()
        except (ValueError, AttributeError) as exc:
            raise InvalidDateError(
                f"Invalid time format: {time_str}. Expected HH:MM or HH:MM:SS"
            ) from exc

    def _normalize_gender(self, gender: str) -> int:
        """Convert accepted gender values to lasotuvi format: 1=male, -1=female."""
        gender_lower = gender.lower().strip()
        if gender_lower in ("male", "nam", "0"):
            return 1
        if gender_lower in ("female", "nữ", "nu", "1"):
            return -1
        raise InvalidDateError(f"Invalid gender: {gender}. Expected 'male' or 'female'")

    def _to_lasotuvi_hour(self, hour_24: int) -> int:
        """Convert a 0-23 clock hour to lasotuvi's 1-12 earthly-branch hour."""
        if hour_24 == 23:
            return 1
        return ((hour_24 + 1) // 2) + 1

    def _normalize_output(
        self,
        raw_chart: Dict[str, Any],
        birth_date: str,
        birth_time: str,
        gender: str,
        label: Optional[str],
    ) -> Dict[str, Any]:
        """Normalize LasoTuviService output to the internal chart schema."""
        palace_data = raw_chart.get("thapNhiCung", [])
        return {
            "chart_type": "TUVI",
            "version": "1.0",
            "metadata": {
                "label": label or "Lá số Tử Vi",
                "birth_date": birth_date,
                "birth_time": birth_time,
                "gender": gender,
                "calculated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "personal_info": raw_chart.get("personalInfo"),
                "destiny_info": raw_chart.get("destinyInfo"),
            },
            "palaces": self._normalize_palaces(palace_data),
            "stars": self._normalize_stars(palace_data),
            "thien_can": raw_chart.get("thienCan"),
            "dia_chi": raw_chart.get("diaChi"),
            "lunar_date": raw_chart.get("lunarDate"),
            "raw_data": raw_chart,
        }

    def _normalize_palaces(self, palace_data: Any) -> Dict[str, Any]:
        """Normalize the 12 palace list to a dict keyed by canonical palace name."""
        normalized = {}
        for palace_info in palace_data:
            palace_name = self._canonical_palace_name(palace_info.get("cungChu", ""))
            normalized[palace_name] = {
                "name": palace_name,
                "stars": [
                    star.get("saoTen", "")
                    for star in palace_info.get("cungSao", [])
                    if star.get("saoTen")
                ],
                "star_details": self._normalize_palace_stars(palace_info.get("cungSao", [])),
                "star_groups": self._group_palace_stars(palace_info.get("cungSao", [])),
                "position": palace_info.get("cungSo"),
                "attributes": {
                    "dia_chi": palace_info.get("diaChi") or palace_info.get("cungTen"),
                    "element": palace_info.get("hanhCung"),
                    "yin_yang": palace_info.get("amDuong"),
                    "dai_han": palace_info.get("daiHan"),
                    "dai_han_age": palace_info.get("tuoiDaiHan") or palace_info.get("daiHan"),
                    "tieu_han": palace_info.get("tieuHan"),
                    "luu_nien_dai_van": palace_info.get("luuNienDaiVan"),
                    "trang_sinh": palace_info.get("trangSinh"),
                    "has_than": palace_info.get("coThan", palace_info.get("coThhan")),
                },
            }
        return normalized

    def _normalize_stars(self, palace_data: Any) -> Dict[str, Any]:
        """Normalize all stars from palace lists into a dict keyed by star name."""
        normalized = {}
        for palace_info in palace_data:
            palace_name = self._canonical_palace_name(palace_info.get("cungChu", ""))
            for star_info in palace_info.get("cungSao", []):
                star_name = star_info.get("saoTen")
                if not star_name:
                    continue

                normalized[star_name] = {
                    "name": star_name,
                    "palace": palace_name,
                    "brightness": star_info.get("saoDacTinh"),
                    "category": (
                        "Chính Tinh" if star_name in self.MAJOR_STARS else "Phụ Tinh"
                    ),
                    "attributes": {
                        "id": star_info.get("saoID"),
                        "brightness_code": star_info.get("saoDacTinhCode"),
                        "color": star_info.get("saoColor"),
                        "quality": star_info.get("saoTinhChat"),
                    },
                }
        return normalized

    def _normalize_palace_stars(self, stars: Any) -> list[Dict[str, Any]]:
        normalized = []
        for star_info in stars:
            star_name = star_info.get("saoTen")
            if not star_name:
                continue
            normalized.append({
                "name": star_name,
                "brightness": star_info.get("saoDacTinh"),
                "brightness_code": star_info.get("saoDacTinhCode"),
                "category": star_info.get("saoNhom") or (
                    "ChÃ­nh Tinh" if star_name in self.MAJOR_STARS else "Phá»¥ Tinh"
                ),
                "color": star_info.get("saoColor"),
                "quality": star_info.get("saoTinhChat"),
                "id": star_info.get("saoID"),
            })
        return normalized

    def _group_palace_stars(self, stars: Any) -> Dict[str, list[Dict[str, Any]]]:
        groups = {
            "chinh_tinh": [],
            "phu_tinh": [],
            "khac": [],
        }
        for star in self._normalize_palace_stars(stars):
            category = self._strip_accents(str(star.get("category", ""))).lower()
            if "chinh" in category:
                groups["chinh_tinh"].append(star)
            elif "phu" in category or "trung" in category or "bang" in category:
                groups["phu_tinh"].append(star)
            else:
                groups["khac"].append(star)
        return groups

    def _strip_accents(self, value: str) -> str:
        replacements = {
            "á": "a", "à": "a", "ả": "a", "ã": "a", "ạ": "a",
            "ă": "a", "ắ": "a", "ằ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
            "â": "a", "ấ": "a", "ầ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
            "é": "e", "è": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
            "ê": "e", "ế": "e", "ề": "e", "ể": "e", "ễ": "e", "ệ": "e",
            "í": "i", "ì": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
            "ó": "o", "ò": "o", "ỏ": "o", "õ": "o", "ọ": "o",
            "ô": "o", "ố": "o", "ồ": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
            "ơ": "o", "ớ": "o", "ờ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
            "ú": "u", "ù": "u", "ủ": "u", "ũ": "u", "ụ": "u",
            "ư": "u", "ứ": "u", "ừ": "u", "ử": "u", "ữ": "u", "ự": "u",
            "ý": "y", "ỳ": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
            "đ": "d",
        }
        return "".join(replacements.get(char, char) for char in value)

    def _canonical_palace_name(self, palace_name: str) -> str:
        normalized_name = palace_name.strip().lower()
        return self.PALACE_NAME_MAP.get(normalized_name, palace_name)
