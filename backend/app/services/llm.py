"""
AI explanation layer — LLM explains the pre-computed score.
Never recalculates or contradicts the risk engine (Section 10).
"""

from __future__ import annotations

from typing import Optional, Tuple

import httpx

from app.config import Settings, get_settings
from app.models.schemas import AdvisoryRequest, AdvisoryResponse
from app.utils.errors import AppError, LLMConfigError, UpstreamTimeoutError

SYSTEM_PROMPT = """You are a public health advisor. You will be given a person's profile,
current environmental conditions, a pre-calculated exposure score, and
a recommended lower-exposure time window. Write a 2-3 sentence
plain-English advisory that explains WHY the score is what it is and
what the person should concretely do, referencing their specific
condition, occupation, PM2.5 / AQI levels, and the recommended time window.
When the notes say a PM2.5 spike bonus was already applied, mention the elevated
fine-particle load in plain English — do not invent a different score.
Do not recalculate or contradict the given score. Avoid generic phrases like
"stay safe" without specifics."""


def build_user_prompt(req: AdvisoryRequest) -> str:
    p = req.profile
    pm25_note = (
        "- PM2.5 spike bonus (+0.5 on base risk) WAS already applied because "
        f"PM2.5 is {req.pm25} µg/m³ (> 90). Cite the particle load; do not add more."
        if float(req.pm25) > 90
        else (
            "- No PM2.5 spike bonus (PM2.5 ≤ 90). Still mention the PM2.5 reading "
            "when it helps explain respiratory risk."
        )
    )
    return f"""Current conditions:
- Temperature: {req.temperature}°C
- AQI (US): {req.aqi}
- PM2.5: {req.pm25} µg/m³

Profile:
- Age group: {p.age_group.value}
- Health condition: {p.health_condition.value}
- Occupation: {p.occupation.value}

Calculated exposure score: {req.score} ({req.label.value})
Recommended lower-exposure window: {req.window}

Scoring notes (already applied — do not recalculate):
- Base risk from US AQI band; +1 heat if temp > 35°C
{pm25_note}

Write a personalized health advisory for this person for today."""


class AdvisoryService:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def _resolve_provider(self) -> Tuple[str, str]:
        """Returns (provider, api_key)."""
        preferred = (self.settings.llm_provider or "auto").lower().strip()
        groq = (self.settings.groq_api_key or "").strip()
        gemini = (self.settings.gemini_api_key or "").strip()

        if preferred == "groq":
            if not groq:
                raise LLMConfigError()
            return "groq", groq
        if preferred == "gemini":
            if not gemini:
                raise LLMConfigError()
            return "gemini", gemini

        # auto: prefer Groq (fast), then Gemini
        if groq:
            return "groq", groq
        if gemini:
            return "gemini", gemini
        raise LLMConfigError()

    async def generate(self, req: AdvisoryRequest) -> AdvisoryResponse:
        provider, key = self._resolve_provider()
        user_prompt = build_user_prompt(req)

        if provider == "groq":
            text, model = await self._groq(key, user_prompt)
        else:
            text, model = await self._gemini(key, user_prompt)

        return AdvisoryResponse(
            advisory_text=text.strip(),
            provider=provider,
            model=model,
        )

    async def _groq(self, api_key: str, user_prompt: str) -> Tuple[str, str]:
        model = self.settings.groq_model
        payload = {
            "model": model,
            "temperature": 0.4,
            "max_tokens": 220,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.http_timeout) as client:
                resp = await client.post(
                    self.settings.groq_url, json=payload, headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException as exc:
            raise UpstreamTimeoutError("Groq") from exc
        except httpx.HTTPStatusError as exc:
            raise AppError(
                f"Groq API error: HTTP {exc.response.status_code}",
                status_code=502,
                code="llm_upstream_error",
            ) from exc

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AppError(
                "Groq returned an unexpected response shape",
                status_code=502,
                code="llm_bad_response",
            ) from exc
        return text, model

    async def _gemini(self, api_key: str, user_prompt: str) -> Tuple[str, str]:
        model = self.settings.gemini_model
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1024,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.http_timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException as exc:
            raise UpstreamTimeoutError("Gemini") from exc
        except httpx.HTTPStatusError as exc:
            detail = ""
            try:
                detail = exc.response.json().get("error", {}).get("message", "")
            except Exception:
                detail = (exc.response.text or "")[:240]
            raise AppError(
                f"Gemini API error: HTTP {exc.response.status_code}"
                + (f" — {detail}" if detail else ""),
                status_code=502,
                code="llm_upstream_error",
            ) from exc

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AppError(
                "Gemini returned an unexpected response shape",
                status_code=502,
                code="llm_bad_response",
            ) from exc
        return text, model
