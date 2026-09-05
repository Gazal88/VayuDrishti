"""
FastAPI Router — POST /advisory endpoint.

Contract (agreed with Person 1):
    POST /advisory
      in:  {conditions, profile, score, label, window}
      out: {advisory_text: str}

Person 1 integrates this by adding to their main app:
    from advisory_engine import advisory_router
    app.include_router(advisory_router)
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from .advisory_service import AdvisoryService

logger = logging.getLogger(__name__)

# ── FastAPI Router ──────────────────────────────────────────────────────
router = APIRouter(tags=["advisory"])

# Lazy-init to avoid crashing at import time if API key isn't set yet
_service: AdvisoryService | None = None


def _get_service() -> AdvisoryService:
    """Lazy-initialize the AdvisoryService on first request."""
    global _service
    if _service is None:
        _service = AdvisoryService()
    return _service


# ── Request / Response Models ───────────────────────────────────────────

class Conditions(BaseModel):
    """Current weather and air quality data from Open-Meteo APIs."""
    temperature: float = Field(..., description="Temperature in °C")
    aqi: int = Field(..., description="US AQI value")
    pm25: float = Field(..., description="PM2.5 concentration in µg/m³")


class Profile(BaseModel):
    """User's health/occupation profile (Section 6 of PS4 doc)."""
    age_group: str = Field(
        ...,
        description="One of: 18-30, 31-50, 51-65, 65+",
        examples=["18-30", "31-50", "51-65", "65+"],
    )
    health_condition: str = Field(
        ...,
        description="One of: none, asthma, heart_condition, pregnant, other",
        examples=["none", "asthma", "heart_condition", "pregnant"],
    )
    occupation: str = Field(
        ...,
        description="One of: desk_job, outdoor_worker, student, elderly_caregiver",
        examples=["desk_job", "outdoor_worker", "student"],
    )


class ExposureWindow(BaseModel):
    """Best lower-exposure window from Person 2's sliding-window algorithm."""
    start: str = Field(..., description="Window start time, e.g. '6:00 AM'")
    end: str = Field(..., description="Window end time, e.g. '8:00 AM'")
    predicted_aqi: float = Field(
        ..., description="Predicted AQI during this window"
    )


class AdvisoryRequest(BaseModel):
    """
    Full request body matching the Person 1 ↔ Person 3 contract.
    """
    conditions: Conditions
    profile: Profile
    score: float = Field(
        ..., ge=0, le=10, description="Exposure risk score (0–10) from risk engine"
    )
    label: str = Field(
        ...,
        description="Risk label: Low, Moderate, High, or Very High",
        examples=["Low", "Moderate", "High", "Very High"],
    )
    window: Optional[ExposureWindow] = Field(
        None,
        description="Optional best lower-exposure window from sliding-window algorithm",
    )


class AdvisoryResponse(BaseModel):
    """Response containing the AI-generated advisory text."""
    advisory_text: str = Field(
        ..., description="Personalized 2–3 sentence health advisory"
    )


# ── Endpoint ────────────────────────────────────────────────────────────

@router.post("/advisory", response_model=AdvisoryResponse)
async def generate_advisory(request: AdvisoryRequest):
    """
    Generate a personalized health advisory using AI.

    Takes current weather/AQI conditions, a user's health profile, and
    a risk score from the deterministic engine, then uses an LLM to
    produce a specific, actionable 2–3 sentence advisory.
    """
    try:
        service = _get_service()
        advisory_text = service.generate_advisory(
            conditions=request.conditions.model_dump(),
            profile=request.profile.model_dump(),
            score=request.score,
            label=request.label,
            window=request.window.model_dump() if request.window else None,
        )
        return AdvisoryResponse(advisory_text=advisory_text)

    except ValueError as e:
        logger.warning("Validation error: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    except RuntimeError as e:
        logger.error("Advisory generation failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail=f"Advisory generation temporarily unavailable: {e}",
        )

    except Exception as e:
        logger.exception("Unexpected error in /advisory")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating the advisory.",
        )
