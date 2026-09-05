"""
Deterministic Exposure Score Calculator for VayuDrishti (PS-4 Role 2).
Implements Section 8: Deterministic Exposure Score - Core Logic.
"""

from typing import Any, Dict, Optional, Tuple, Union
from .constants import (
    AGE_ALIASES,
    AGE_MULTIPLIERS,
    BASE_AQI_THRESHOLDS,
    CONDITION_ALIASES,
    CONDITION_MULTIPLIERS,
    HEAT_COMPOUND_INCREMENT,
    HEAT_COMPOUND_TEMP_CELSIUS,
    LABEL_HIGH,
    LABEL_LOW,
    LABEL_MODERATE,
    LABEL_VERY_HIGH,
    OCCUPATION_ALIASES,
    OCCUPATION_MULTIPLIERS,
    RISK_COLORS,
    SCORE_THRESHOLDS,
)


def estimate_aqi_from_pm25(pm25: float) -> float:
    """
    Standard US EPA linear interpolation to estimate AQI from PM2.5 (µg/m³).
    Used as an automatic fallback if AQI is missing or invalid from the API.
    """
    if pm25 < 0:
        return 0.0

    # EPA PM2.5 (C_low, C_high, I_low, I_high)
    breakpoints = [
        (0.0, 12.0, 0.0, 50.0),
        (12.1, 35.4, 51.0, 100.0),
        (35.5, 55.4, 101.0, 150.0),
        (55.5, 150.4, 151.0, 200.0),
        (150.5, 250.4, 201.0, 300.0),
        (250.5, 350.4, 301.0, 400.0),
        (350.5, 500.4, 401.0, 500.0),
    ]

    for c_low, c_high, i_low, i_high in breakpoints:
        if pm25 <= c_high:
            # Linear interpolation: I = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low
            return round(((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low, 1)

    # For extreme values > 500 µg/m³
    return 500.0


def calculate_base_risk(
    aqi: Optional[float] = None,
    pm25: Optional[float] = None,
    temp: Optional[float] = None,
) -> Tuple[int, Dict[str, Any]]:
    """
    Calculates the base environmental risk score (1 to 5, +1 for heat > 35°C).

    Base risk mapping:
      AQI 0–50    -> base 1
      AQI 51–100  -> base 2
      AQI 101–150 -> base 3
      AQI 151–200 -> base 4
      AQI 201+    -> base 5
      (+1 to base if temperature > 35°C)

    Returns:
      (total_base_risk, debug_metadata)
    """
    effective_aqi = aqi

    if effective_aqi is None or effective_aqi < 0:
        if pm25 is not None and pm25 >= 0:
            effective_aqi = estimate_aqi_from_pm25(pm25)
        else:
            effective_aqi = 0.0

    raw_base = 1
    for upper_limit, score in BASE_AQI_THRESHOLDS:
        if effective_aqi <= upper_limit:
            raw_base = score
            break

    heat_compound = False
    effective_temp = float(temp) if temp is not None else 0.0
    if effective_temp > HEAT_COMPOUND_TEMP_CELSIUS:
        raw_base += HEAT_COMPOUND_INCREMENT
        heat_compound = True

    metadata = {
        "effective_aqi": round(float(effective_aqi), 1),
        "aqi_base": raw_base - (HEAT_COMPOUND_INCREMENT if heat_compound else 0),
        "heat_compounded": heat_compound,
        "temperature": effective_temp,
        "total_base_risk": raw_base,
    }

    return raw_base, metadata


def normalize_input(value: Optional[str], alias_map: Dict[str, str], default: str) -> str:
    """Normalizes string inputs, handling whitespace, case, and aliases."""
    if not value or not isinstance(value, str):
        return default
    cleaned = value.strip().lower().replace("-", "_").replace(" ", "_")
    # check direct cleaned value
    if cleaned in alias_map:
        return alias_map[cleaned]
    # check original lowercase stripped
    orig = value.strip().lower()
    if orig in alias_map:
        return alias_map[orig]
    return default


def get_profile_multipliers(
    age_group: Optional[str] = None,
    health_condition: Optional[str] = None,
    occupation: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resolves the multipliers for a given user profile.
    Safe against invalid/missing inputs, defaulting to 1.0 (baseline/neutral).
    """
    norm_age = normalize_input(age_group, AGE_ALIASES, default="18-30")
    norm_condition = normalize_input(health_condition, CONDITION_ALIASES, default="none")
    norm_occupation = normalize_input(occupation, OCCUPATION_ALIASES, default="desk_job")

    cond_mult = CONDITION_MULTIPLIERS.get(norm_condition, 1.0)
    occ_mult = OCCUPATION_MULTIPLIERS.get(norm_occupation, 1.0)
    age_mult = AGE_MULTIPLIERS.get(norm_age, 1.0)

    total_profile_multiplier = round(cond_mult * occ_mult * age_mult, 4)

    return {
        "age_group": norm_age,
        "health_condition": norm_condition,
        "occupation": norm_occupation,
        "condition_multiplier": cond_mult,
        "occupation_multiplier": occ_mult,
        "age_multiplier": age_mult,
        "combined_multiplier": total_profile_multiplier,
    }


def bucket_score(score: float) -> str:
    """
    Maps exposure score to categorical label:
      0.0 – 2.5 -> Low
      2.5 – 5.0 -> Moderate (score == 5.0 -> Moderate)
      5.0 – 8.0 -> High (score > 5.0 and <= 8.0 -> High)
      8.0+      -> Very High
    """
    for upper_bound, label in SCORE_THRESHOLDS:
        if score <= upper_bound:
            return label
    return LABEL_VERY_HIGH


def calculate_exposure(
    aqi: Union[float, int, None],
    pm25: Union[float, int, None] = None,
    temp: Union[float, int, None] = None,
    age_group: Optional[str] = None,
    health_condition: Optional[str] = None,
    occupation: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Main entry point for Section 8: Deterministic Exposure Scoring.

    Contract agreed between Person 1 & Person 2:
      calculate_exposure(aqi, pm25, temp/temperature, age_group, health_condition, occupation)
        -> {"score": float, "label": str, "breakdown": {...}}

    Compatible with both Role 2 specifications and Person 1's FastAPI Pydantic schema:
      - score: float (rounded to 2 decimal places)
      - label: str ("Low", "Moderate", "High", "Very High")
      - color: str (HEX color code for UI)
      - breakdown: dict satisfying both ScoreBreakdown schema and extended metadata
    """
    # Allow either 'temp' or 'temperature' (for Person 1's router compatibility)
    temperature = kwargs.get("temperature")
    resolved_temp = temperature if temperature is not None else temp

    # Safe float conversion
    safe_aqi = float(aqi) if aqi is not None else None
    safe_pm25 = float(pm25) if pm25 is not None else None
    safe_temp = float(resolved_temp) if resolved_temp is not None else None

    # Handle enum objects if passed (e.g. from Pydantic AgeGroup, HealthCondition, Occupation)
    norm_age_str = getattr(age_group, "value", age_group) if age_group is not None else None
    norm_cond_str = getattr(health_condition, "value", health_condition) if health_condition is not None else None
    norm_occ_str = getattr(occupation, "value", occupation) if occupation is not None else None

    # 1. Base risk
    base_risk, env_meta = calculate_base_risk(aqi=safe_aqi, pm25=safe_pm25, temp=safe_temp)

    # 2. Profile multipliers
    profile_meta = get_profile_multipliers(
        age_group=norm_age_str,
        health_condition=norm_cond_str,
        occupation=norm_occ_str,
    )

    # 3. Final calculation: base_risk × condition × occupation × age
    raw_score = (
        base_risk
        * profile_meta["condition_multiplier"]
        * profile_meta["occupation_multiplier"]
        * profile_meta["age_multiplier"]
    )
    final_score = round(raw_score, 2)

    # 4. Bucketing
    label = bucket_score(final_score)
    color = RISK_COLORS.get(label, "#10B981")

    # Heat bonus integer (1 if heat compounded else 0) for Pydantic ScoreBreakdown compatibility
    heat_bonus = 1 if env_meta["heat_compounded"] else 0
    formula_str = (
        f"({base_risk}{' + 1 heat' if heat_bonus else ''}) x "
        f"{profile_meta['condition_multiplier']} x "
        f"{profile_meta['occupation_multiplier']} x "
        f"{profile_meta['age_multiplier']} = {final_score}"
    )

    # Construct response matching Person 1's contract perfectly
    return {
        "score": final_score,
        "label": label,
        "color": color,
        "breakdown": {
            # Person 1 Pydantic ScoreBreakdown fields
            "base_risk": float(base_risk),
            "heat_bonus": heat_bonus,
            "pm25_bonus": 0.0,
            "condition_multiplier": profile_meta["condition_multiplier"],
            "occupation_multiplier": profile_meta["occupation_multiplier"],
            "age_multiplier": profile_meta["age_multiplier"],
            "formula": formula_str,

            # Extended metadata for Person 3 (LLM) and Person 4 (UI)
            "aqi_component": env_meta["aqi_base"],
            "heat_compounded": env_meta["heat_compounded"],
            "effective_aqi": env_meta["effective_aqi"],
            "temperature": env_meta["temperature"],
            "combined_profile_multiplier": profile_meta["combined_multiplier"],
            "raw_score": raw_score,
        },
    }
