"""
POST /analyze — one-shot endpoint for the demo wow-moment.

City + profile → live conditions + score + best window + AI advisory.
Frontend can call this alone for the fastest integration path.
"""

from fastapi import APIRouter, Request

from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AdvisoryRequest,
    DashboardResponse,
    ExposureScoreResponse,
    HourlyForecastResponse,
    HourlyPoint,
)
from app.services.llm import AdvisoryService
from app.services.openmeteo import OpenMeteoClient
from app.services.risk_engine import best_lower_exposure_window, calculate_exposure
from app.utils.errors import AppError
from app.utils.ratelimit import advisory_limiter, general_limiter

router = APIRouter(tags=["Analyze"])
meteo = OpenMeteoClient()
advisor = AdvisoryService()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(body: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    advisory_limiter.check(request)   # costs Gemini quota
    dash_raw = await meteo.dashboard(body.city)
    hourly_raw = await meteo.hourly_forecast(body.city)

    aqi = dash_raw.get("aqi")
    pm25 = dash_raw.get("pm25")
    temperature = dash_raw.get("temperature")

    if aqi is None or temperature is None:
        raise AppError(
            "Live conditions incomplete for this location. Try another city.",
            status_code=502,
            code="incomplete_conditions",
        )
    if pm25 is None:
        pm25 = 0.0

    result = calculate_exposure(
        aqi=float(aqi),
        pm25=float(pm25),
        temperature=float(temperature),
        age_group=body.profile.age_group,
        health_condition=body.profile.health_condition,
        occupation=body.profile.occupation,
    )

    best_window = best_lower_exposure_window(
        hourly_raw["hours"],
        age_group=body.profile.age_group,
        health_condition=body.profile.health_condition,
        occupation=body.profile.occupation,
    )

    exposure = ExposureScoreResponse(
        score=result["score"],
        label=result["label"],
        breakdown=result["breakdown"],
        conditions={
            "aqi": aqi,
            "pm25": pm25,
            "temperature": temperature,
        },
        profile=body.profile,
        best_window=best_window,
        city_name=dash_raw["city_name"],
    )

    advisory = None
    if body.include_advisory:
        window_label = best_window.label if best_window else "not available"
        advisory = await advisor.generate(
            AdvisoryRequest(
                temperature=float(temperature),
                aqi=float(aqi),
                pm25=float(pm25),
                profile=body.profile,
                score=result["score"],
                label=result["label"],
                window=window_label,
            )
        )

    hourly = None
    if body.include_hourly:
        hourly = HourlyForecastResponse(
            city_name=hourly_raw["city_name"],
            latitude=hourly_raw["latitude"],
            longitude=hourly_raw["longitude"],
            hours=[HourlyPoint(**h) for h in hourly_raw["hours"]],
        )

    return AnalyzeResponse(
        dashboard=DashboardResponse(**dash_raw),
        exposure=exposure,
        advisory=advisory,
        hourly=hourly,
    )
