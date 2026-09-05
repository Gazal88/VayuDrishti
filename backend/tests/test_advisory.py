"""
Test Advisory Engine -- validates advisory output against 4 contrasting profiles.

This is the Role 3 deliverable that proves the LLM generates visibly
different, profile-specific advisories for the same weather conditions.

Usage:
    1. Copy .env.example to .env and add your API key
    2. pip install -r requirements_role3.txt
    3. python test_advisory.py
"""

import sys
import io

# Fix Windows console encoding for Unicode output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from advisory_engine.advisory_service import AdvisoryService


# -- Same conditions for ALL profiles (the whole point of the demo) ------
CONDITIONS = {
    "temperature": 38,
    "aqi": 180,
    "pm25": 95.0,
}

# -- Best lower-exposure window (from Person 2's sliding-window algo) ----
WINDOW = {
    "start": "6:00 AM",
    "end": "8:00 AM",
    "predicted_aqi": 85,
}

# -- 4 contrasting profiles ---------------------------------------------
# These are chosen to produce maximally different advisories on the same
# conditions, which is the strongest demo moment (see Demo Script step 4).
TEST_PROFILES = [
    {
        "name": "Healthy Desk Worker (young)",
        "profile": {
            "age_group": "18-30",
            "health_condition": "none",
            "occupation": "desk_job",
        },
        "score": 3.2,
        "label": "Low",
    },
    {
        "name": "Asthma + Outdoor Worker (middle-aged)",
        "profile": {
            "age_group": "31-50",
            "health_condition": "asthma",
            "occupation": "outdoor_worker",
        },
        "score": 8.7,
        "label": "Very High",
    },
    {
        "name": "Elderly with Heart Condition",
        "profile": {
            "age_group": "65+",
            "health_condition": "heart_condition",
            "occupation": "desk_job",
        },
        "score": 7.1,
        "label": "High",
    },
    {
        "name": "Pregnant Student",
        "profile": {
            "age_group": "18-30",
            "health_condition": "pregnant",
            "occupation": "student",
        },
        "score": 6.5,
        "label": "High",
    },
]


def main():
    service = AdvisoryService()

    print("=" * 72)
    print("  ADVISORY ENGINE TEST -- Same Conditions, Different Profiles")
    print(
        f"  Conditions: {CONDITIONS['temperature']} C  |  "
        f"AQI {CONDITIONS['aqi']}  |  "
        f"PM2.5 {CONDITIONS['pm25']} ug/m3"
    )
    print(
        f"  Best Window: {WINDOW['start']} - {WINDOW['end']} "
        f"(predicted AQI ~{WINDOW['predicted_aqi']})"
    )
    print("=" * 72)

    for i, test in enumerate(TEST_PROFILES, 1):
        print(f"\n{'-' * 72}")
        print(f"  Profile {i}: {test['name']}")
        print(f"  Score: {test['score']}/10  |  Label: {test['label']}")
        print(f"{'-' * 72}")

        advisory = service.generate_advisory(
            conditions=CONDITIONS,
            profile=test["profile"],
            score=test["score"],
            label=test["label"],
            window=WINDOW,
        )

        print(f"\n  Advisory:\n")
        # Wrap advisory text nicely
        for line in advisory.strip().split("\n"):
            print(f"    {line}")
        print()

    print("=" * 72)
    print("  All 4 profiles tested -- compare advisories above.")
    print("  The outputs should be VISIBLY DIFFERENT for each profile.")
    print("=" * 72)


if __name__ == "__main__":
    main()
