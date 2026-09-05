"""POST /advisory — uses app/services/llm.py (httpx, no SDK)."""

from fastapi import APIRouter, Request

from app.models.schemas import AdvisoryRequest, AdvisoryResponse
from app.utils.ratelimit import advisory_limiter

router = APIRouter(tags=["Advisory"])

# Lazy init — created on first request so settings are fully loaded
_service = None

def _get_service():
    global _service
    if _service is None:
        from app.services.llm import AdvisoryService
        _service = AdvisoryService()
    return _service


@router.post("/advisory", response_model=AdvisoryResponse)
async def post_advisory(body: AdvisoryRequest, request: Request) -> AdvisoryResponse:
    advisory_limiter.check(request)
    return await _get_service().generate(body)
