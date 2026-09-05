"""
VayuDrishti Risk Engine (PS-4 Role 2)
Deterministic scoring math and best lower-exposure window algorithm.
"""

from .calculator import (
    bucket_score,
    calculate_base_risk,
    calculate_exposure,
    estimate_aqi_from_pm25,
    get_profile_multipliers,
)
from .constants import (
    AGE_MULTIPLIERS,
    BASE_AQI_THRESHOLDS,
    CONDITION_MULTIPLIERS,
    HEAT_COMPOUND_INCREMENT,
    HEAT_COMPOUND_TEMP_CELSIUS,
    LABEL_HIGH,
    LABEL_LOW,
    LABEL_MODERATE,
    LABEL_VERY_HIGH,
    OCCUPATION_MULTIPLIERS,
    RISK_COLORS,
    SCORE_THRESHOLDS,
)
from .window import (
    BestWindowResult,
    best_lower_exposure_window,
    find_best_window,
    format_hour_12h,
    normalize_hourly_data,
    parse_hour_from_time_str,
)

__all__ = [
    "calculate_exposure",
    "find_best_window",
    "best_lower_exposure_window",
    "BestWindowResult",
    "calculate_base_risk",
    "get_profile_multipliers",
    "estimate_aqi_from_pm25",
    "bucket_score",
    "format_hour_12h",
    "parse_hour_from_time_str",
    "normalize_hourly_data",
    "BASE_AQI_THRESHOLDS",
    "HEAT_COMPOUND_TEMP_CELSIUS",
    "HEAT_COMPOUND_INCREMENT",
    "CONDITION_MULTIPLIERS",
    "OCCUPATION_MULTIPLIERS",
    "AGE_MULTIPLIERS",
    "SCORE_THRESHOLDS",
    "RISK_COLORS",
    "LABEL_LOW",
    "LABEL_MODERATE",
    "LABEL_HIGH",
    "LABEL_VERY_HIGH",
]

__version__ = "1.0.0"
 