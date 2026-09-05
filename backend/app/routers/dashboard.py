"""GET /dashboard — live weather + AQI for a city."""

from fastapi import APIRouter, Query, Request

from app.models.schemas import DashboardResponse
from app.services.openmeteo import OpenMeteoClient
from app.utils.ratelimit import general_limiter

router = APIRouter(tags=["Dashboard"])
client = OpenMeteoClient()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    request: Request,
    city: str = Query(..., min_length=1, description="City name, e.g. Delhi"),
) -> DashboardResponse:
    general_limiter.check(request)
    data = await client.dashboard(city)
    return DashboardResponse(**data)
