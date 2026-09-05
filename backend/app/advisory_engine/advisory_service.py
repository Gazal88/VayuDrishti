"""
Advisory Service — the core orchestrator for Role 3.

Takes in conditions + profile + risk score and returns a personalized
health advisory by calling the configured LLM with a carefully
engineered prompt.
"""

import logging
from pathlib import Path
from dotenv import load_dotenv
from .llm_client import LLMClient
from .prompt_builder import SYSTEM_PROMPT, build_user_prompt

# Belt-and-suspenders: ensure .env is loaded before LLMClient reads os.environ
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env", override=True)

logger = logging.getLogger(__name__)


class AdvisoryService:
    """
    Main service class for generating personalized health advisories.

    Usage
    -----
    >>> service = AdvisoryService()
    >>> text = service.generate_advisory(
    ...     conditions={"temperature": 38, "aqi": 180, "pm25": 95.0},
    ...     profile={"age_group": "31-50", "health_condition": "asthma", "occupation": "outdoor_worker"},
    ...     score=8.7,
    ...     label="Very High",
    ...     window={"start": "6:00 AM", "end": "8:00 AM", "predicted_aqi": 85}
    ... )
    """

    def __init__(self):
        self._llm = LLMClient()
        logger.info("AdvisoryService initialized")

    def generate_advisory(
        self,
        conditions: dict,
        profile: dict,
        score: float,
        label: str,
        window: dict | None = None,
    ) -> str:
        """
        Generate a personalized health advisory.

        Parameters
        ----------
        conditions : dict
            Current weather/AQI data. Expected keys: temperature, aqi, pm25.
        profile : dict
            User's health profile. Expected keys: age_group, health_condition, occupation.
        score : float
            Numeric exposure risk score (0–10) from Person 2's risk engine.
        label : str
            Risk label: "Low", "Moderate", "High", or "Very High".
        window : dict or None
            Optional best lower-exposure window from Person 2's sliding-window
            algorithm. Expected keys: start, end, predicted_aqi.

        Returns
        -------
        str
            The generated advisory text (2–3 sentences, plain English).

        Raises
        ------
        RuntimeError
            If the LLM call fails.
        ValueError
            If required fields are missing from conditions or profile.
        """
        # ── Validate inputs ─────────────────────────────────────────────
        self._validate_conditions(conditions)
        self._validate_profile(profile)

        # ── Build prompt ────────────────────────────────────────────────
        user_prompt = build_user_prompt(conditions, profile, score, label, window)
        logger.debug("User prompt built:\n%s", user_prompt)

        # ── Call LLM ────────────────────────────────────────────────────
        advisory_text = self._llm.generate(SYSTEM_PROMPT, user_prompt)
        logger.info(
            "Advisory generated for %s / %s — score %.1f (%s)",
            profile.get("health_condition"),
            profile.get("occupation"),
            score,
            label,
        )

        return advisory_text

    # ── Input Validation ────────────────────────────────────────────────

    @staticmethod
    def _validate_conditions(conditions: dict):
        required = ["temperature", "aqi", "pm25"]
        missing = [k for k in required if k not in conditions]
        if missing:
            raise ValueError(
                f"Missing required condition fields: {', '.join(missing)}"
            )

    @staticmethod
    def _validate_profile(profile: dict):
        required = ["age_group", "health_condition", "occupation"]
        missing = [k for k in required if k not in profile]
        if missing:
            raise ValueError(
                f"Missing required profile fields: {', '.join(missing)}"
            )
