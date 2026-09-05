import os
import logging
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env", override=True)

logger = logging.getLogger(__name__)
_TIMEOUT = 30.0


class LLMClient:
    def __init__(self):
        self._gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self._groq_key   = os.environ.get("GROQ_API_KEY", "").strip()
        self._provider   = os.environ.get("LLM_PROVIDER", "gemini").lower().strip()
        self._model      = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash").strip()
        self._temp       = float(os.environ.get("LLM_TEMPERATURE", "0.7"))
        self._max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "500"))

        if not self._gemini_key and not self._groq_key:
            raise ValueError(
                f"No API key found. Set GEMINI_API_KEY or GROQ_API_KEY in backend/.env"
            )

        logger.info("LLMClient ready — provider=%s model=%s", self._provider, self._model)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            if self._provider == "groq" and self._groq_key:
                return self._call_groq(system_prompt, user_prompt)
            return self._call_gemini(system_prompt, user_prompt)
        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            raise RuntimeError(f"Advisory generation failed: {e}") from e

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        if not self._gemini_key:
            raise ValueError("GEMINI_API_KEY is empty")

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._gemini_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature":     self._temp,
                "maxOutputTokens": self._max_tokens,
            },
        }

        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error("Gemini %s: %s", resp.status_code, resp.text[:300])
            resp.raise_for_status()
            data = resp.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"Unexpected Gemini response: {data}") from e

    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model":       "llama-3.1-8b-instant",
            "temperature": self._temp,
            "max_tokens":  self._max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._groq_key}",
            "Content-Type":  "application/json",
        }
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"Unexpected Groq response: {data}") from e
