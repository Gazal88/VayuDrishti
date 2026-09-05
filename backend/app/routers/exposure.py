"""POST /exposure-score — deterministic personalized exposure + best window."""

from fastapi import APIRouter

from app.models.schemas import ExposureScoreRequest, ExposureScoreResponse
from app.services.openmeteo import OpenMeteoClient
from app.services.risk_engine import best_lower_exposure_window, calculate_exposure
from app.utils.errors import AppError

router = APIRouter(tags=["Exposure"])
client = OpenMeteoClient()


@router.post("/exposure-score", response_model=ExposureScoreResponse)
async def post_exposure_score(body: ExposureScoreRequest) -> ExposureScoreResponse:
    city_name = None
    aqi = body.aqi
    pm25 = body.pm25
    temperature = body.temperature

    if body.city:
        dash = await client.dashboard(body.city)
        city_name = dash["city_name"]
        aqi = dash.get("aqi") if aqi is None else aqi
        pm25 = dash.get("pm25") if pm25 is None else pm25
        temperature = dash.get("temperature") if temperature is None else temperature

    if aqi is None or temperature is None:
        raise AppError(
            "aqi and temperature are required (pass them directly or provide city).",
            status_code=422,
            code="missing_conditions",
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

    best_window = None
    if body.include_best_window and body.city:
        hourly = await client.hourly_forecast(body.city)
        best_window = best_lower_exposure_window(
            hourly["hours"],
            age_group=body.profile.age_group,
            health_condition=body.profile.health_condition,
            occupation=body.profile.occupation,
        )

    return ExposureScoreResponse(
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
        city_name=city_name,
    )
