"""
Sliding-Window Best Lower-Exposure Time Window Algorithm (PS-4 Role 2).
Implements Section 9 of PS4_Final_Documentation.md.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from .calculator import bucket_score, calculate_exposure, get_profile_multipliers


def format_hour_12h(hour: int) -> str:
    """Formats an hour (0-23) into 12-hour format e.g. 7 -> '7 AM', 19 -> '7 PM', 0 -> '12 AM'."""
    normalized_hour = hour % 24
    if normalized_hour == 0:
        return "12 AM"
    elif normalized_hour < 12:
        return f"{normalized_hour} AM"
    elif normalized_hour == 12:
        return "12 PM"
    else:
        return f"{normalized_hour - 12} PM"


def parse_hour_from_time_str(time_str: str) -> Tuple[int, str]:
    """
    Extracts the hour (0-23) and formatted 12h label from an ISO or HH:MM time string.
    Examples:
      '2026-09-04T19:00' -> (19, '7 PM')
      '2026-09-04 19:00' -> (19, '7 PM')
      '19:00'            -> (19, '7 PM')
      '7'                -> (7, '7 AM')
    """
    cleaned = str(time_str).strip()

    # Case 1: Pure integer or digit string
    if cleaned.isdigit():
        h = int(cleaned) % 24
        return h, format_hour_12h(h)

    # Case 2: ISO datetime format (e.g. '2026-09-04T19:00' or '2026-09-04 19:00')
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%H:%M"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.hour, format_hour_12h(dt.hour)
        except ValueError:
            pass

    # Case 3: Extract hour from 'T19:00' or similar
    if "T" in cleaned:
        time_part = cleaned.split("T")[-1]
        hour_part = time_part.split(":")[0]
        if hour_part.isdigit():
            h = int(hour_part) % 24
            return h, format_hour_12h(h)

    # Default fallback
    return 0, "12 AM"


def normalize_hourly_data(
    hourly_data: Union[Dict[str, List[Any]], List[Dict[str, Any]]],
    default_temp: float = 25.0,
) -> List[Dict[str, Any]]:
    """
    Normalizes hourly input from either Open-Meteo API response structure or list of records.

    Accepts:
      1. Open-Meteo structure:
         {
             "time": ["2026-09-04T00:00", ...],
             "us_aqi": [110, ...],
             "pm2_5": [35.0, ...],
             "temperature_2m": [30.0, ...] # optional
         }
      2. List of dicts:
         [
             {"time": "2026-09-04T00:00", "aqi": 110, "pm25": 35.0, "temp": 30.0},
             ...
         ]
    """
    normalized: List[Dict[str, Any]] = []

    if isinstance(hourly_data, dict):
        times = hourly_data.get("time", [])
        aqis = hourly_data.get("us_aqi", hourly_data.get("aqi", []))
        pm25s = hourly_data.get("pm2_5", hourly_data.get("pm25", []))
        temps = hourly_data.get("temperature_2m", hourly_data.get("temp", hourly_data.get("temperature", [])))

        count = len(times) if times else max(len(aqis), len(pm25s))
        for i in range(count):
            t_str = times[i] if i < len(times) else f"{i:02d}:00"
            aqi_val = aqis[i] if i < len(aqis) else None
            pm25_val = pm25s[i] if i < len(pm25s) else None
            temp_val = temps[i] if i < len(temps) else default_temp

            normalized.append({
                "time": str(t_str),
                "aqi": aqi_val,
                "pm25": pm25_val,
                "temp": temp_val if temp_val is not None else default_temp,
            })

    elif isinstance(hourly_data, list):
        for idx, item in enumerate(hourly_data):
            if isinstance(item, dict):
                t_str = item.get("time", f"{idx:02d}:00")
                aqi_val = item.get("aqi", item.get("us_aqi"))
                pm25_val = item.get("pm25", item.get("pm2_5"))
                temp_val = item.get("temp", item.get("temperature", item.get("temperature_2m", default_temp)))

                normalized.append({
                    "time": str(t_str),
                    "aqi": aqi_val,
                    "pm25": pm25_val,
                    "temp": temp_val if temp_val is not None else default_temp,
                })

    return normalized


def find_best_window(
    hourly_data: Union[Dict[str, List[Any]], List[Dict[str, Any]]],
    age_group: Optional[str] = "18-30",
    health_condition: Optional[str] = "none",
    occupation: Optional[str] = "desk_job",
    window_hours: int = 2,
    default_temp: float = 25.0,
) -> Dict[str, Any]:
    """
    Finds the continuous time window of length `window_hours` (default 2h)
    with the lowest average personalized exposure score.

    Algorithm (Section 9):
      1. Normalize hourly conditions for 24h.
      2. Compute personalized exposure score for each hour using active profile multipliers.
      3. Slide a 2-hour window across the hourly scores and compute the window average.
      4. Find the window with the minimum average score.
      5. Return formatted window string (e.g. '7 PM – 9 PM'), average score, label, and hourly series.
    """
    hourly_records = normalize_hourly_data(hourly_data, default_temp=default_temp)

    if not hourly_records:
        return {
            "best_window": "N/A",
            "window_24h": "N/A",
            "average_score": 0.0,
            "label": "Low",
            "start_time": "",
            "end_time": "",
            "hourly_scores": [],
        }

    # 1. Calculate personalized exposure score for each hour
    hourly_evaluations: List[Dict[str, Any]] = []
    for item in hourly_records:
        res = calculate_exposure(
            aqi=item["aqi"],
            pm25=item["pm25"],
            temp=item["temp"],
            age_group=age_group,
            health_condition=health_condition,
            occupation=occupation,
        )
        h_val, h_12_label = parse_hour_from_time_str(item["time"])
        hourly_evaluations.append({
            "time": item["time"],
            "hour": h_val,
            "hour_label": h_12_label,
            "score": res["score"],
            "label": res["label"],
            "color": res["color"],
            "aqi": res["breakdown"]["effective_aqi"],
            "temp": res["breakdown"]["temperature"],
        })

    n = len(hourly_evaluations)
    # If fewer hours than window size, evaluate over available hours
    effective_window = min(window_hours, n)
    if effective_window <= 0:
        effective_window = 1

    best_start_idx = 0
    min_avg_score = float("inf")

    # 2. Slide window across hourly scores
    num_windows = n - effective_window + 1
    for i in range(num_windows):
        window_scores = [hourly_evaluations[i + j]["score"] for j in range(effective_window)]
        avg_score = sum(window_scores) / float(effective_window)

        # We look for the lowest score
        if avg_score < min_avg_score:
            min_avg_score = avg_score
            best_start_idx = i

    best_end_idx = best_start_idx + effective_window - 1

    # 3. Format time labels
    start_rec = hourly_evaluations[best_start_idx]
    start_hour = start_rec["hour"]
    end_hour = (start_hour + effective_window) % 24

    start_12h = format_hour_12h(start_hour)
    end_12h = format_hour_12h(end_hour)

    best_window_str = f"{start_12h} – {end_12h}"
    window_24h_str = f"{start_hour:02d}:00 – {end_hour:02d}:00"

    final_avg = round(min_avg_score, 2)
    final_label = bucket_score(final_avg)

    return {
        "best_window": best_window_str,
        "window_24h": window_24h_str,
        "average_score": final_avg,
        "label": final_label,
        "start_time": start_rec["time"],
        "end_time": hourly_evaluations[best_end_idx]["time"],
        "start_hour": start_hour,
        "end_hour": end_hour,
        "hourly_scores": hourly_evaluations,
    }


class BestWindowResult(dict):
    """
    Container supporting both attribute-style (window.label) and dict-style (window['label'])
    access for seamless compatibility with Person 1's routers and Pydantic schemas.
    """
    def __init__(self, start: str, end: str, label: str, average_score: float, average_label: str):
        super().__init__(
            start=start,
            end=end,
            label=label,
            average_score=average_score,
            average_label=average_label,
        )
        self.start = start
        self.end = end
        self.label = label
        self.average_score = average_score
        self.average_label = average_label

    def __repr__(self) -> str:
        return f"BestWindow(start={self.start!r}, end={self.end!r}, label={self.label!r}, average_score={self.average_score}, average_label={self.average_label!r})"


def best_lower_exposure_window(
    hourly: Union[Sequence[Dict[str, Any]], Dict[str, List[Any]]],
    age_group: Optional[str] = "18-30",
    health_condition: Optional[str] = "none",
    occupation: Optional[str] = "desk_job",
    window_hours: int = 2,
    now: Optional[datetime] = None,
) -> Optional[BestWindowResult]:
    """
    Section 9 sliding window algorithm formatted for Person 1's backend routers.
    Accepts hourly records, optionally filters for future/current hours (via `now`),
    and returns a BestWindowResult (supporting both .attribute and ['key'] access).
    """
    records = normalize_hourly_data(hourly)
    if not records or len(records) < window_hours:
        return None

    # Handle past hours filtering if now is provided
    pool = records
    if now is not None:
        future = []
        for r in records:
            t_val = r["time"]
            for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
                try:
                    dt = datetime.strptime(str(t_val), fmt)
                    if dt >= now.replace(minute=0, second=0, microsecond=0):
                        future.append(r)
                    break
                except ValueError:
                    pass
        if len(future) >= window_hours:
            pool = future

    res = find_best_window(
        hourly_data=pool,
        age_group=age_group,
        health_condition=health_condition,
        occupation=occupation,
        window_hours=window_hours,
    )

    if not res or not res.get("start_time"):
        return None

    # Format label compatible with ASCII and unicode
    label = f"{res['best_window']}"

    return BestWindowResult(
        start=res["start_time"],
        end=res["end_time"],
        label=label,
        average_score=res["average_score"],
        average_label=res["label"],
    )

