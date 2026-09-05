"""
Prompt Builder — constructs system and user prompts for advisory generation.

Based on PS4 Documentation Section 7 (AI Advisory — Prompt Design) and
the agreed contract:
    POST /advisory
      in:  {conditions, profile, score, label, window}
      out: {advisory_text: str}
"""

# ── System Prompt ───────────────────────────────────────────────────────
# Follows Section 7 of PS4_Documentation.md — conditions the LLM to act
# as a public health advisor producing specific, actionable guidance.

SYSTEM_PROMPT = (
    "You are a public health advisor specializing in air quality and weather-related "
    "health risks. Given current weather/AQI data, a person's health profile, and their "
    "computed exposure risk score, write a 2–3 sentence plain-English advisory.\n\n"
    "Rules:\n"
    "1. Be specific and actionable — mention concrete times, activities to avoid or do, "
    "and explain WHY based on their specific condition and occupation.\n"
    "2. Reference the exposure risk score and label to ground your advice "
    "(e.g., 'Your exposure score is 8.7/10 — Very High').\n"
    "3. If a best lower-exposure window is provided, recommend it explicitly.\n"
    "4. Do NOT use generic phrases like 'stay safe' or 'take care' without specifics.\n"
    "5. Do NOT repeat the raw data back — the user can already see it on the dashboard. "
    "Focus on what they should DO differently.\n"
    "6. Keep tone calm but clear — avoid alarmism, but don't downplay genuine risk."
)


def build_user_prompt(
    conditions: dict,
    profile: dict,
    score: float,
    label: str,
    window: dict | None = None,
) -> str:
    """
    Build the user-facing prompt that gets sent alongside the system prompt.

    Parameters
    ----------
    conditions : dict
        Must contain keys: temperature, aqi, pm25.
    profile : dict
        Must contain keys: age_group, health_condition, occupation.
    score : float
        Numeric exposure risk score from Person 2's risk engine.
    label : str
        Human-readable risk label (Low / Moderate / High / Very High).
    window : dict or None
        Optional best lower-exposure window with keys: start, end, predicted_aqi.

    Returns
    -------
    str
        The fully formatted user prompt.
    """

    # ── Current conditions block ────────────────────────────────────────
    prompt_parts = [
        "Current conditions:",
        f"- Temperature: {conditions.get('temperature', 'N/A')}°C",
        f"- AQI (US): {conditions.get('aqi', 'N/A')}",
        f"- PM2.5: {conditions.get('pm25', 'N/A')} µg/m³",
        "",
    ]

    # ── Profile block ───────────────────────────────────────────────────
    prompt_parts += [
        "Profile:",
        f"- Age group: {profile.get('age_group', 'N/A')}",
        f"- Health condition: {profile.get('health_condition', 'none')}",
        f"- Occupation: {profile.get('occupation', 'N/A')}",
        "",
    ]

    # ── Risk score block ────────────────────────────────────────────────
    prompt_parts += [
        f"Exposure Risk Score: {score}/10 ({label})",
        "",
    ]

    # ── Best window block (optional) ────────────────────────────────────
    if window:
        prompt_parts += [
            "Best Lower-Exposure Window:",
            f"- Time: {window.get('start', 'N/A')} to {window.get('end', 'N/A')}",
            f"- Predicted AQI during window: ~{window.get('predicted_aqi', 'N/A')}",
            "",
        ]

    # ── Final instruction ───────────────────────────────────────────────
    prompt_parts.append(
        "Write a personalized health advisory for this person for today."
    )

    return "\n".join(prompt_parts)
