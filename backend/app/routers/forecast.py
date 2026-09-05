"""GET /hourly-forecast — 24h AQI/PM2.5/temp for best-window + charts."""

from fastapi import APIRouter, Query

from app.models.schemas import HourlyForecastResponse, HourlyPoint
from app.services.openmeteo import OpenMeteoClient

router = APIRouter(tags=["Forecast"])
client = OpenMeteoClient()


@router.get("/hourly-forecast", response_model=HourlyForecastResponse)
async def get_hourly_forecast(
    city: str = Query(..., min_length=1, description="City name, e.g. Delhi"),
) -> HourlyForecastResponse:
    data = await client.hourly_forecast(city)
    return HourlyForecastResponse(
        city_name=data["city_name"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        hours=[HourlyPoint(**h) for h in data["hours"]],
    )
