"""
Advisory Engine — Role 3: AI Explanation Lead
Owns: LLM prompt (Groq/Gemini), personalized advisory generation.

This module provides the POST /advisory endpoint and all LLM integration
for generating personalized health advisories based on weather/AQI conditions
and user health profiles.
"""

from .advisory_service import AdvisoryService
from .router import router as advisory_router

__all__ = ["AdvisoryService", "advisory_router"]
