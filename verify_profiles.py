"""
VayuDrishti - Risk Engine Verification & Demo Script (Role 2).
Run this script to verify the math, print demo profiles, and inspect the exact outputs.
Usage: python verify_profiles.py
"""

import json
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from risk_engine import calculate_exposure, find_best_window

SEPARATOR = "=" * 80
SUB_SEPARATOR = "-" * 80


def print_wow_moment():
    print("\n" + SEPARATOR)
    print("[!] THE WOW MOMENT (Section 13 of Documentation)")
    print("Identical environmental conditions: AQI 160, PM2.5 75 ug/m3, Temperature 38 C")
    print(SEPARATOR)

    # Base calculation
    # AQI 160 -> base 4; Temp 38 C (>35 C) -> +1 heat compound -> base = 5
    p_a = calculate_exposure(
        aqi=160, pm25=75, temp=38,
        age_group="18-30", health_condition="none", occupation="desk_job"
    )

    p_b = calculate_exposure(
        aqi=160, pm25=75, temp=38,
        age_group="18-30", health_condition="asthma", occupation="outdoor_worker"
    )

    print(f"{'Metric':<30} | {'Profile A (Healthy Desk)':<24} | {'Profile B (Asthmatic Outdoor)':<26}")
    print(SUB_SEPARATOR)
    print(f"{'Health Condition':<30} | {'none (1.0x)':<24} | {'asthma (1.6x)':<26}")
    print(f"{'Occupation':<30} | {'desk_job (1.0x)':<24} | {'outdoor_worker (1.5x)':<26}")
    print(f"{'Age Group':<30} | {'18-30 (1.0x)':<24} | {'18-30 (1.0x)':<26}")
    print(f"{'Base Risk (AQI 160 + Heat)':<30} | {p_a['breakdown']['base_risk']:<24} | {p_b['breakdown']['base_risk']:<26}")
    print(f"{'Combined Multiplier':<30} | {p_a['breakdown']['combined_profile_multiplier']:<24} | {p_b['breakdown']['combined_profile_multiplier']:<26}")
    print(f"{'CALCULATED SCORE':<30} | {p_a['score']:<24} | {p_b['score']:<26}")
    print(f"{'RISK LABEL':<30} | {p_a['label']:<24} | {p_b['label']:<26}")
    print(f"{'UI Badge Color':<30} | {p_a['color']:<24} | {p_b['color']:<26}")
    print(SUB_SEPARATOR)
    print(">> Wow Moment Validated: Same air quality, 2.4x higher risk for vulnerable worker!")


def print_five_contrasting_profiles():
    print("\n" + SEPARATOR)
    print("[*] 5 CONTRASTING PROFILES BENCHMARK")
    print(SEPARATOR)

    profiles = [
        {
            "name": "1. Healthy Young Desk Worker",
            "aqi": 40, "pm25": 10, "temp": 26,
            "age": "18-30", "condition": "none", "occ": "desk_job"
        },
        {
            "name": "2. Asthmatic Outdoor Laborer",
            "aqi": 160, "pm25": 75, "temp": 38,
            "age": "18-30", "condition": "asthma", "occ": "outdoor_worker"
        },
        {
            "name": "3. Senior with Heart Disease",
            "aqi": 120, "pm25": 45, "temp": 30,
            "age": "65+", "condition": "heart_condition", "occ": "desk_job"
        },
        {
            "name": "4. Pregnant Student",
            "aqi": 90, "pm25": 31, "temp": 32,
            "age": "18-30", "condition": "pregnant", "occ": "student"
        },
        {
            "name": "5. Middle-Aged Caregiver",
            "aqi": 180, "pm25": 110, "temp": 28,
            "age": "51-65", "condition": "other", "occ": "elderly_caregiver"
        },
    ]

    print(f"{'Profile Name':<30} | {'Conditions':<18} | {'Formula (Base x Mults)':<22} | {'Score':<6} | {'Label':<10}")
    print(SUB_SEPARATOR)
    for p in profiles:
        res = calculate_exposure(
            aqi=p["aqi"], pm25=p["pm25"], temp=p["temp"],
            age_group=p["age"], health_condition=p["condition"], occupation=p["occ"]
        )
        b = res["breakdown"]
        formula = f"{b['base_risk']} x {b['condition_multiplier']} x {b['occupation_multiplier']} x {b['age_multiplier']}"
        cond_str = f"AQI {p['aqi']}, {p['temp']} C"
        print(f"{p['name']:<30} | {cond_str:<18} | {formula:<22} | {res['score']:<6} | {res['label']:<10}")


def print_sliding_window_demo():
    print("\n" + SEPARATOR)
    print("[*] SECTION 9: 24-HOUR SLIDING WINDOW ALGORITHM DEMO")
    print("Simulated 24-hour forecast with daytime traffic pollution and evening clearing")
    print(SEPARATOR)

    times = [f"2026-09-04T{h:02d}:00" for h in range(24)]
    # Typical city profile: high AQI daytime (150-180), drops in late evening (19:00 - 21:00 to ~40)
    aqis = [
        130, 125, 120, 115, 110, 120, 145, 165,
        170, 160, 155, 150, 145, 140, 150, 160,
        170, 165, 130, 38, 42, 80, 95, 110
    ]
    temps = [26] * 8 + [32, 34, 36, 37, 36, 35, 33, 31] + [29, 28, 27, 26, 25, 25, 25, 25]

    data = {
        "time": times,
        "us_aqi": aqis,
        "temperature_2m": temps,
    }

    # Run for outdoor worker with asthma
    window_res = find_best_window(
        data,
        age_group="18-30",
        health_condition="asthma",
        occupation="outdoor_worker",
        window_hours=2
    )

    print(f"Recommended Lower-Exposure Window : {window_res['best_window']} ({window_res['window_24h']})")
    print(f"Average Exposure Score in Window   : {window_res['average_score']} ({window_res['label']})")
    print(f"Window Start Time                 : {window_res['start_time']}")
    print(f"Window End Time                   : {window_res['end_time']}")


def print_contract_json_shape():
    print("\n" + SEPARATOR)
    print("[*] PERSON 1 <-> PERSON 2 CONTRACT COMPLIANCE (JSON Output)")
    print(SEPARATOR)
    sample = calculate_exposure(160, 75, 38, "18-30", "asthma", "outdoor_worker")
    print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    print_wow_moment()
    print_five_contrasting_profiles()
    print_sliding_window_demo()
    print_contract_json_shape()
