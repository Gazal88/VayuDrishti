"""HTTP / domain errors with clean JSON for the frontend."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "app_error"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class CityNotFoundError(AppError):
    def __init__(self, city: str):
        super().__init__(
            message=f'No location found for "{city}". Try a different city name.',
            status_code=404,
            code="city_not_found",
        )


class UpstreamTimeoutError(AppError):
    def __init__(self, service: str = "Open-Meteo"):
        super().__init__(
            message=f"{service} timed out. Please try again in a moment.",
            status_code=504,
            code="upstream_timeout",
        )


class UpstreamEmptyError(AppError):
    def __init__(self, detail: str = "Upstream returned empty data"):
        super().__init__(
            message=detail,
            status_code=502,
            code="upstream_empty",
        )


class LLMConfigError(AppError):
    def __init__(self):
        super().__init__(
            message=(
                "No LLM API key configured. Set GROQ_API_KEY or GEMINI_API_KEY "
                "in backend/.env (see .env.example)."
            ),
            status_code=503,
            code="llm_not_configured",
        )


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "code": exc.code, "message": exc.message},
    )


def raise_http(status: int, message: str, code: str = "error") -> None:
    raise HTTPException(
        status_code=status,
        detail={"error": True, "code": code, "message": message},
    )
