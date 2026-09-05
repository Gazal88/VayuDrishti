"""Application settings — free-tier friendly, no paid services."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute path so settings load correctly regardless of working directory
_ENV_FILE = str(Path(__file__).resolve().parent.parent / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "VayuDrishti API"
    app_version: str = "1.0.0"

    # Optional: set this to restrict API access when deployed publicly.
    # Leave empty for local dev (no key required).
    app_api_key: str = ""

    groq_api_key: str = ""
    gemini_api_key: str = ""
    llm_provider: str = "auto"  # groq | gemini | auto

    # Read from env CORS_ORIGINS (comma-separated). Include deployed frontend
    # origin (Vercel / Netlify / ngrok) alongside localhost for remote demos.
    cors_origins: str = (
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    )
    http_timeout: float = 45.0

    # Open-Meteo (no keys)
    geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    weather_url: str = "https://api.open-meteo.com/v1/forecast"
    air_quality_url: str = "https://air-quality-api.open-meteo.com/v1/air-quality"

    # Groq / Gemini endpoints
    groq_url: str = "https://api.groq.com/openai/v1/chat/completions"
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-3.6-flash"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    return Settings()
