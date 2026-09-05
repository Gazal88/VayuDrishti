"""
VayuDrishti API — AI-Powered Personalized Weather & AQI Health Advisory
Origin Hackathon PS-4 | Backend / API Integration Lead deliverable
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import advisory, analyze, dashboard, exposure, forecast
from app.utils.errors import AppError, app_error_handler

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Live Open-Meteo weather + AQI, deterministic exposure scoring, "
        "best lower-exposure window, and LLM explanation layer. "
        "Data by Open-Meteo (CC-BY 4.0)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Optional API key guard ────────────────────────────────────────────────
# Set APP_API_KEY in .env to restrict access when deployed publicly.
# Leave it empty (default) for local dev — no key required.
@app.middleware("http")
async def api_key_guard(request: Request, call_next):
    required = (settings.app_api_key or "").strip()
    # No key configured → open access (local dev / hackathon demo)
    if not required:
        return await call_next(request)
    # Health + docs endpoints are always public
    if request.url.path in ("/", "/health", "/docs", "/redoc", "/openapi.json"):
        return await call_next(request)
    # Check header or query param
    provided = (
        request.headers.get("X-API-Key")
        or request.query_params.get("api_key")
        or ""
    ).strip()
    if provided != required:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return await call_next(request)

app.add_exception_handler(AppError, app_error_handler)

app.include_router(dashboard.router)
app.include_router(forecast.router)
app.include_router(exposure.router)
app.include_router(advisory.router)
app.include_router(analyze.router)


@app.get("/", tags=["Health"])
@app.head("/", tags=["Health"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "ok",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": settings.app_version}
