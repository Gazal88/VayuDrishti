"""Unit tests for the deterministic risk engine — judge-ready math."""

import sys
from pathlib import Path

# Allow `pytest` from backend/ without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.risk_engine import (
    best_lower_exposure_window,
    calculate_exposure,
    label_for_score,
)


def test_healthy_desk_vs_asthma_outdoor_wow_moment():
    """Same conditions, different profiles → clearly different labels."""
    aqi, pm25, temp = 160, 75, 38  # demo beat numbers

    desk = calculate_exposure(
        aqi, pm25, temp, "18-30", "none", "desk_job"
    )
    # base 4 + heat 1 = 5 × 1 × 1 × 1 = 5.0 → Moderate (<5? wait 5.0 is Moderate if <5 is Moderate and <8 is High)
    # label: score < 2.5 Low, < 5 Moderate, < 8 High, else Very High
    # 5.0 → High (not < 5)
    assert desk["score"] == 5.0
    assert desk["label"].value == "High"

    asthma = calculate_exposure(
        aqi, pm25, temp, "18-30", "asthma", "outdoor_worker"
    )
    # 5 × 1.6 × 1.5 × 1.0 = 12.0 → Very High
    assert asthma["score"] == 12.0
    assert asthma["label"].value == "Very High"
    assert asthma["score"] > desk["score"]


def test_no_heat_bonus_under_35():
    result = calculate_exposure(80, 20, 34, "18-30", "none", "desk_job")
    # base 2, no heat → 2.0 Low
    assert result["score"] == 2.0
    assert result["breakdown"].heat_bonus == 0
    assert result["label"].value == "Low"


def test_heat_bonus_over_35():
    result = calculate_exposure(80, 20, 36, "18-30", "none", "desk_job")
    assert result["score"] == 3.0
    assert result["breakdown"].heat_bonus == 1


def test_elderly_multiplier():
    young = calculate_exposure(120, 40, 30, "18-30", "none", "desk_job")
    old = calculate_exposure(120, 40, 30, "65+", "none", "desk_job")
    # base 3; young 3.0, old 3 * 1.35 = 4.05
    assert young["score"] == 3.0
    assert old["score"] == 4.05


def test_label_buckets():
    assert label_for_score(2.4).value == "Low"
    assert label_for_score(2.5).value == "Moderate"
    assert label_for_score(4.9).value == "Moderate"
    assert label_for_score(5.0).value == "High"
    assert label_for_score(8.0).value == "Very High"


def test_pm25_bonus_above_threshold_raises_pre_multiplier_base():
    """PM2.5 > 90 adds +0.5 to base before multipliers; <= 90 does not."""
    # Same AQI band / temp / profile — only PM2.5 crosses the spike line
    low_pm = calculate_exposure(120, 90, 30, "18-30", "none", "desk_job")
    high_pm = calculate_exposure(120, 90.1, 30, "18-30", "none", "desk_job")

    assert low_pm["breakdown"].pm25_bonus == 0.0
    assert low_pm["score"] == 3.0  # base 3 only

    assert high_pm["breakdown"].pm25_bonus == 0.5
    assert high_pm["score"] == 3.5  # (3 + 0.5) x 1 x 1 x 1
    assert high_pm["score"] - low_pm["score"] == 0.5
    assert "0.5 pm25" in high_pm["breakdown"].formula


def test_pm25_bonus_scales_with_profile_multipliers():
    """Bonus sits on base, then profile multipliers apply (asthma outdoor)."""
    # (3 + 0.5) x 1.6 x 1.5 x 1.0 = 8.4
    result = calculate_exposure(
        120, 100, 30, "18-30", "asthma", "outdoor_worker"
    )
    assert result["breakdown"].pm25_bonus == 0.5
    assert result["score"] == 8.4


def test_best_window_picks_lowest_average():

    hourly = [
        {"time": "2026-09-04T10:00", "aqi": 180, "pm25": 80, "temperature": 30},
        {"time": "2026-09-04T11:00", "aqi": 170, "pm25": 70, "temperature": 30},
        {"time": "2026-09-04T12:00", "aqi": 50, "pm25": 10, "temperature": 30},
        {"time": "2026-09-04T13:00", "aqi": 40, "pm25": 8, "temperature": 30},
        {"time": "2026-09-04T14:00", "aqi": 160, "pm25": 60, "temperature": 30},
    ]
    window = best_lower_exposure_window(
        hourly, "18-30", "none", "desk_job", window_hours=2
    )
    assert window is not None
    assert window.start == "2026-09-04T12:00"
    assert "12 PM" in window.label and "2 PM" in window.label
    # Force "now" before the clean hours so past filtering still picks 12-2
    from datetime import datetime

    window2 = best_lower_exposure_window(
        hourly,
        "18-30",
        "none",
        "desk_job",
        window_hours=2,
        now=datetime(2026, 9, 4, 11, 0),
    )
    assert window2 is not None
    assert window2.start == "2026-09-04T12:00"
