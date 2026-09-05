"""Pydantic contracts — agree these with Frontend / Risk / AI leads in first 15 min."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ─── Profile enums (match Section 7 exactly) ─────────────────────────────────


class AgeGroup(str, Enum):
    AGE_18_30 = "18-30"
    AGE_31_50 = "31-50"
    AGE_51_65 = "51-65"
    AGE_65_PLUS = "65+"


class HealthCondition(str, Enum):
    NONE = "none"
    ASTHMA = "asthma"
    HEART_CONDITION = "heart_condition"
    PREGNANT = "pregnant"
    OTHER = "other"


class Occupation(str, Enum):
    DESK_JOB = "desk_job"
    OUTDOOR_WORKER = "outdoor_worker"
    STUDENT = "student"
    ELDERLY_CAREGIVER = "elderly_caregiver"


class RiskLabel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"


# ─── Shared profile ───────────────────────────────────────────────────────────


class UserProfile(BaseModel):
    age_group: AgeGroup
    health_condition: HealthCondition
    occupation: Occupation


# ─── GET /dashboard ───────────────────────────────────────────────────────────


class DashboardResponse(BaseModel):
    """Person 1 ↔ Person 4 contract."""

    city_name: str
    country: Optional[str] = None
    latitude: float
    longitude: float
    temperature: float = Field(..., description="°C")
    humidity: Optional[float] = Field(None, description="%")
    weather_code: Optional[int] = None
    weather_description: Optional[str] = None
    aqi: Optional[float] = Field(None, description="US AQI")
    european_aqi: Optional[float] = None
    pm25: Optional[float] = Field(None, description="µg/m³")
    pm10: Optional[float] = Field(None, description="µg/m³")
    timezone: Optional[str] = None
    attribution: str = "Weather & air quality data by Open-Meteo (CC-BY 4.0)"


# ─── GET /hourly-forecast ─────────────────────────────────────────────────────


class HourlyPoint(BaseModel):
    time: str
    temperature: Optional[float] = None
    aqi: Optional[float] = None
    pm25: Optional[float] = None


class HourlyForecastResponse(BaseModel):
    city_name: str
    latitude: float
    longitude: float
    hours: List[HourlyPoint]
    attribution: str = "Weather & air quality data by Open-Meteo (CC-BY 4.0)"


# ─── POST /exposure-score ─────────────────────────────────────────────────────


class ExposureScoreRequest(BaseModel):
    """Person 1 ↔ Person 2 contract (+ city for live conditions)."""

    city: Optional[str] = Field(
        None, description="If set, live conditions are fetched for this city"
    )
    # Or pass conditions directly (useful for unit tests / Person 2)
    aqi: Optional[float] = None
    pm25: Optional[float] = None
    temperature: Optional[float] = None
    profile: UserProfile
    include_best_window: bool = True


class ScoreBreakdown(BaseModel):
    base_risk: float
    heat_bonus: int
    pm25_bonus: float = 0.0
    condition_multiplier: float
    occupation_multiplier: float
    age_multiplier: float
    formula: str


class BestWindow(BaseModel):
    start: str
    end: str
    label: str = Field(..., description='e.g. "7 PM – 9 PM"')
    average_score: float
    average_label: RiskLabel


class ExposureScoreResponse(BaseModel):
    score: float
    label: RiskLabel
    breakdown: ScoreBreakdown
    conditions: dict
    profile: UserProfile
    best_window: Optional[BestWindow] = None
    city_name: Optional[str] = None


# ─── POST /advisory ───────────────────────────────────────────────────────────


class AdvisoryRequest(BaseModel):
    """Person 1 ↔ Person 3 contract."""

    temperature: float
    aqi: float
    pm25: float
    profile: UserProfile
    score: float
    label: RiskLabel
    window: str = Field(..., description='e.g. "7 PM – 9 PM"')


class AdvisoryResponse(BaseModel):
    advisory_text: str
    provider: str
    model: str


# ─── POST /analyze (one-shot for frontend wow demo) ───────────────────────────


class AnalyzeRequest(BaseModel):
    city: str
    profile: UserProfile
    include_advisory: bool = True
    include_hourly: bool = False


class AnalyzeResponse(BaseModel):
    dashboard: DashboardResponse
    exposure: ExposureScoreResponse
    advisory: Optional[AdvisoryResponse] = None
    hourly: Optional[HourlyForecastResponse] = None
