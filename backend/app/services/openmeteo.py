"""Open-Meteo client — geocoding, weather, air quality. No API keys."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.config import Settings, get_settings
from app.utils.errors import AppError, CityNotFoundError, UpstreamEmptyError, UpstreamTimeoutError
from app.utils.weather_codes import describe_weather

logger = logging.getLogger(__name__)

_RETRY_DELAY_SEC = 1.0


class OpenMeteoClient:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    async def _get(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """GET with one retry on timeout / 5xx, then raise existing AppErrors."""
        last_exc: Optional[Exception] = None
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.settings.http_timeout) as client:
                    response = await client.get(url, params=params)
                    # Retry once on upstream 5xx; 4xx falls through to raise below
                    if response.status_code >= 500 and attempt == 0:
                        logger.warning(
                            "Open-Meteo HTTP %s on attempt 1 — retrying once in %.0fs",
                            response.status_code,
                            _RETRY_DELAY_SEC,
                        )
                        await asyncio.sleep(_RETRY_DELAY_SEC)
                        continue
                    response.raise_for_status()
                    data = response.json()
                    if not data:
                        raise UpstreamEmptyError("Open-Meteo returned an empty response")
                    return data
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt == 0:
                    logger.warning(
                        "Open-Meteo timeout on attempt 1 — retrying once in %.0fs",
                        _RETRY_DELAY_SEC,
                    )
                    await asyncio.sleep(_RETRY_DELAY_SEC)
                    continue
                raise UpstreamTimeoutError("Open-Meteo") from exc
            except httpx.HTTPStatusError as exc:
                raise UpstreamEmptyError(
                    f"Open-Meteo HTTP {exc.response.status_code}"
                ) from exc
            except AppError:
                raise
            except Exception as exc:
                raise UpstreamEmptyError(f"Open-Meteo request failed: {exc}") from exc

        # Should be unreachable; keep a safe fallback
        raise UpstreamTimeoutError("Open-Meteo") from last_exc

    async def geocode(self, city: str, count: int = 1) -> Dict[str, Any]:
        city = (city or "").strip()
        if not city:
            raise CityNotFoundError(city or "(empty)")

        data = await self._get(
            self.settings.geocoding_url,
            {"name": city, "count": count, "language": "en", "format": "json"},
        )
        results = data.get("results") or []
        if not results:
            raise CityNotFoundError(city)

        hit = results[0]
        return {
            "city_name": hit.get("name") or city,
            "country": hit.get("country"),
            "admin1": hit.get("admin1"),
            "latitude": float(hit["latitude"]),
            "longitude": float(hit["longitude"]),
            "timezone": hit.get("timezone"),
        }

    async def current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        data = await self._get(
            self.settings.weather_url,
            {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code",
                "hourly": "temperature_2m",
                "forecast_days": 2,
                "timezone": "auto",
            },
        )
        current = data.get("current") or {}
        if not current:
            raise UpstreamEmptyError("Weather current block missing")

        code = current.get("weather_code")
        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "weather_code": code,
            "weather_description": describe_weather(code),
            "timezone": data.get("timezone"),
            "hourly_temperature": _zip_hourly(
                data.get("hourly", {}).get("time"),
                data.get("hourly", {}).get("temperature_2m"),
                "temperature",
            ),
        }

    async def current_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        data = await self._get(
            self.settings.air_quality_url,
            {
                "latitude": lat,
                "longitude": lon,
                "current": "pm10,pm2_5,us_aqi,european_aqi",
                "hourly": "pm2_5,us_aqi",
                "forecast_days": 2,
                "timezone": "auto",
            },
        )
        current = data.get("current") or {}
        if not current:
            raise UpstreamEmptyError("Air quality current block missing")

        hourly = data.get("hourly") or {}
        return {
            "aqi": current.get("us_aqi"),
            "european_aqi": current.get("european_aqi"),
            "pm25": current.get("pm2_5"),
            "pm10": current.get("pm10"),
            "timezone": data.get("timezone"),
            "hourly_aqi": _zip_hourly(
                hourly.get("time"), hourly.get("us_aqi"), "aqi"
            ),
            "hourly_pm25": _zip_hourly(
                hourly.get("time"), hourly.get("pm2_5"), "pm25"
            ),
        }

    async def dashboard(self, city: str) -> Dict[str, Any]:
        """Combined geo + weather + AQI — Person 1 ↔ Person 4 contract."""
        geo = await self.geocode(city)
        weather, aqi = await asyncio.gather(
            self.current_weather(geo["latitude"], geo["longitude"]),
            self.current_air_quality(geo["latitude"], geo["longitude"]),
        )
        return {
            "city_name": geo["city_name"],
            "country": geo.get("country"),
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "temperature": weather["temperature"],
            "humidity": weather.get("humidity"),
            "weather_code": weather.get("weather_code"),
            "weather_description": weather.get("weather_description"),
            "aqi": aqi.get("aqi"),
            "european_aqi": aqi.get("european_aqi"),
            "pm25": aqi.get("pm25"),
            "pm10": aqi.get("pm10"),
            "timezone": weather.get("timezone")
            or aqi.get("timezone")
            or geo.get("timezone"),
        }

    async def hourly_forecast(self, city: str) -> Dict[str, Any]:
        """
        Merged hourly series for best-window + timeline chart.

        Weather and air-quality hourly arrays are joined by matching `time`
        strings (never by bare index), so each hour always carries
        temperature + aqi + pm25 keys when the upstream provides them.
        """
        geo = await self.geocode(city)
        weather, aqi = await asyncio.gather(
            self.current_weather(geo["latitude"], geo["longitude"]),
            self.current_air_quality(geo["latitude"], geo["longitude"]),
        )

        # Align by ISO time string — weather and AQ endpoints can differ in length
        temp_by_time = {
            p["time"]: p.get("temperature") for p in weather["hourly_temperature"]
        }
        aqi_by_time = {p["time"]: p.get("aqi") for p in aqi["hourly_aqi"]}
        pm_by_time = {p["time"]: p.get("pm25") for p in aqi["hourly_pm25"]}

        times = sorted(set(temp_by_time) | set(aqi_by_time) | set(pm_by_time))
        hours: List[Dict[str, Any]] = []
        for t in times:
            temperature = temp_by_time.get(t)
            if temperature is None and t in aqi_by_time:
                # Risk engine would otherwise silently assume 30°C — surface it.
                logger.warning(
                    "hourly_forecast: missing temperature for %s (city=%s); "
                    "risk engine will fall back to 30.0°C for this hour",
                    t,
                    geo["city_name"],
                )
            hours.append(
                {
                    "time": t,
                    "temperature": temperature,
                    "aqi": aqi_by_time.get(t),
                    "pm25": pm_by_time.get(t),
                }
            )

        return {
            "city_name": geo["city_name"],
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "hours": hours,
        }


def _zip_hourly(
    times: Optional[List[str]], values: Optional[List[Any]], key: str
) -> List[Dict[str, Any]]:
    if not times or values is None:
        return []
    out: List[Dict[str, Any]] = []
    for i, t in enumerate(times):
        val = values[i] if i < len(values) else None
        out.append({"time": t, key: val})
    return out
