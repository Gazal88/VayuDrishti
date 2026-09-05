"""
Constants and configuration for VayuDrishti Risk Engine (PS-4 Role 2).
Derived directly from Section 8 of PS4_Final_Documentation.md.
"""

from typing import Dict, Tuple

# Base AQI thresholds -> Base Risk
# AQI 0–50    -> base 1
# AQI 51–100  -> base 2
# AQI 101–150 -> base 3
# AQI 151–200 -> base 4
# AQI 201+    -> base 5
BASE_AQI_THRESHOLDS: Tuple[Tuple[float, int], ...] = (
    (50.0, 1),
    (100.0, 2),
    (150.0, 3),
    (200.0, 4),
    (float("inf"), 5),
)

# Heat compounding threshold:
# (+1 to base if temperature > 35°C — heat compounds respiratory/cardiac load)
HEAT_COMPOUND_TEMP_CELSIUS: float = 35.0
HEAT_COMPOUND_INCREMENT: int = 1

# Health condition multipliers
CONDITION_MULTIPLIERS: Dict[str, float] = {
    "none": 1.0,
    "asthma": 1.6,
    "heart_condition": 1.5,
    "pregnant": 1.3,
    "other": 1.2,
}

# Occupation multipliers
OCCUPATION_MULTIPLIERS: Dict[str, float] = {
    "desk_job": 1.0,
    "student": 1.1,
    "elderly_caregiver": 1.15,
    "outdoor_worker": 1.5,
}

# Age group multipliers
AGE_MULTIPLIERS: Dict[str, float] = {
    "18-30": 1.0,
    "31-50": 1.05,
    "51-65": 1.2,
    "65+": 1.35,
}

# Risk score bucketing for display
# 0 – 2.5   -> Low
# 2.5 – 5.0 -> Moderate (Note: 5.0 is Moderate per Section 13 wow moment)
# 5.0 – 8.0 -> High
# 8.0+      -> Very High
LABEL_LOW: str = "Low"
LABEL_MODERATE: str = "Moderate"
LABEL_HIGH: str = "High"
LABEL_VERY_HIGH: str = "Very High"

SCORE_THRESHOLDS: Tuple[Tuple[float, str], ...] = (
    (2.5, LABEL_LOW),
    (5.0, LABEL_MODERATE),
    (8.0, LABEL_HIGH),
    (float("inf"), LABEL_VERY_HIGH),
)

# Color codes associated with labels (useful for Person 4 / UI Lead)
RISK_COLORS: Dict[str, str] = {
    LABEL_LOW: "#10B981",       # Emerald Green
    LABEL_MODERATE: "#F59E0B",  # Amber / Yellow
    LABEL_HIGH: "#F97316",      # Orange
    LABEL_VERY_HIGH: "#EF4444", # Red
}

# Aliases for input normalization (handles spaces, dashes, alternate namings)
CONDITION_ALIASES: Dict[str, str] = {
    "none": "none",
    "healthy": "none",
    "normal": "none",
    "no": "none",
    "asthma": "asthma",
    "asthmatic": "asthma",
    "heart_condition": "heart_condition",
    "heart condition": "heart_condition",
    "cardiac": "heart_condition",
    "heart": "heart_condition",
    "pregnant": "pregnant",
    "pregnancy": "pregnant",
    "other": "other",
}

OCCUPATION_ALIASES: Dict[str, str] = {
    "desk_job": "desk_job",
    "desk job": "desk_job",
    "desk": "desk_job",
    "office": "desk_job",
    "student": "student",
    "elderly_caregiver": "elderly_caregiver",
    "elderly caregiver": "elderly_caregiver",
    "caregiver": "elderly_caregiver",
    "outdoor_worker": "outdoor_worker",
    "outdoor worker": "outdoor_worker",
    "outdoor": "outdoor_worker",
    "field_worker": "outdoor_worker",
    "driver": "outdoor_worker",
    "construction": "outdoor_worker",
}

AGE_ALIASES: Dict[str, str] = {
    "18-30": "18-30",
    "18 - 30": "18-30",
    "young_adult": "18-30",
    "31-50": "31-50",
    "31 - 50": "31-50",
    "adult": "31-50",
    "51-65": "51-65",
    "51 - 65": "51-65",
    "middle_aged": "51-65",
    "65+": "65+",
    "65 +": "65+",
    "65 plus": "65+",
    "elderly": "65+",
    "senior": "65+",
}
