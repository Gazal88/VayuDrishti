"""Bridge between Role 2 Risk Engine and FastAPI schemas."""
from app.models.schemas import BestWindow, RiskLabel, ScoreBreakdown
from app.risk_engine import (
    best_lower_exposure_window as _best_window,
    calculate_exposure as _calc,
    bucket_score,
)

def label_for_score(score: float) -> RiskLabel:
    return RiskLabel(bucket_score(score))

def calculate_exposure(aqi, pm25, temperature, age_group, health_condition, occupation):
    res = _calc(
        aqi=aqi,
        pm25=pm25,
        temperature=temperature,
        age_group=age_group,
        health_condition=health_condition,
        occupation=occupation,
    )
    res["label"] = RiskLabel(res["label"])
    res["breakdown"] = ScoreBreakdown(**res["breakdown"])
    return res

def best_lower_exposure_window(hourly, age_group, health_condition, occupation, window_hours=2, now=None):
    w = _best_window(
        hourly,
        age_group=age_group,
        health_condition=health_condition,
        occupation=occupation,
        window_hours=window_hours,
        now=now,
    )
    if not w:
        return None
    return BestWindow(
        start=w.start,
        end=w.end,
        label=w.label,
        average_score=w.average_score,
        average_label=RiskLabel(w.average_label),
    )