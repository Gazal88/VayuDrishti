"""
Unit tests for VayuDrishti Risk Engine (PS-4 Role 2).
Covers Section 8 (Deterministic Scoring), Section 9 (Sliding Window),
Section 13 (The Wow Moment), and 5+ contrasting profiles.
"""

import unittest
from risk_engine import (
    calculate_exposure,
    calculate_base_risk,
    find_best_window,
    estimate_aqi_from_pm25,
    bucket_score,
    LABEL_LOW,
    LABEL_MODERATE,
    LABEL_HIGH,
    LABEL_VERY_HIGH,
)


class TestRiskEngineCore(unittest.TestCase):

    def test_section_13_wow_moment(self):
        """
        Tests the exact 'Wow Moment' described in Section 13:
        Conditions: AQI 160, Temp 38°C (base = 4 + 1 = 5)
        Profile A: Adult (18-30), no condition, desk job -> 5.0 (Moderate)
        Profile B: Adult (18-30), asthma, outdoor worker -> 12.0 (Very High)
        """
        # Profile A: Healthy Desk Worker
        res_a = calculate_exposure(
            aqi=160,
            pm25=75.0,
            temp=38.0,
            age_group="18-30",
            health_condition="none",
            occupation="desk_job",
        )
        self.assertEqual(res_a["score"], 5.0)
        self.assertEqual(res_a["label"], LABEL_MODERATE)
        self.assertEqual(res_a["breakdown"]["base_risk"], 5)
        self.assertTrue(res_a["breakdown"]["heat_compounded"])

        # Profile B: Asthmatic Outdoor Worker on IDENTICAL conditions
        res_b = calculate_exposure(
            aqi=160,
            pm25=75.0,
            temp=38.0,
            age_group="18-30",
            health_condition="asthma",
            occupation="outdoor_worker",
        )
        # 5 * 1.6 (asthma) * 1.5 (outdoor) * 1.0 (18-30) = 12.0
        self.assertEqual(res_b["score"], 12.0)
        self.assertEqual(res_b["label"], LABEL_VERY_HIGH)

        # Confirm dramatic divergence on same conditions
        self.assertGreater(res_b["score"], res_a["score"] * 2)

    def test_five_contrasting_profiles(self):
        """
        Verifies 5 contrasting profiles demonstrating full demographic and health coverage.
        """
        # Profile 1: Healthy Young Desk Worker (Good Air, Normal Temp)
        # Base: AQI 40 -> 1, Temp 26°C -> +0 = 1. Multipliers: 1.0 * 1.0 * 1.0 = 1.0 (Low)
        p1 = calculate_exposure(40, 10, 26, "18-30", "none", "desk_job")
        self.assertEqual(p1["score"], 1.0)
        self.assertEqual(p1["label"], LABEL_LOW)

        # Profile 2: Asthmatic Outdoor Laborer (Severe Air, Heat)
        # Base: AQI 160 -> 4 + 1 (38°C) = 5. Multipliers: 1.6 * 1.5 * 1.0 = 2.4. Score = 12.0 (Very High)
        p2 = calculate_exposure(160, 75, 38, "18-30", "asthma", "outdoor_worker")
        self.assertEqual(p2["score"], 12.0)
        self.assertEqual(p2["label"], LABEL_VERY_HIGH)

        # Profile 3: Senior Citizen with Heart Disease (Moderate-High Air)
        # Base: AQI 120 -> 3, Temp 30°C -> +0 = 3. Multipliers: 1.5 * 1.0 * 1.35 = 2.025.
        # Score = 3 * 2.025 = 6.075 -> 6.08 (High)
        p3 = calculate_exposure(120, 45, 30, "65+", "heart_condition", "desk_job")
        self.assertEqual(p3["score"], 6.08)
        self.assertEqual(p3["label"], LABEL_HIGH)

        # Profile 4: Pregnant Student (Moderate Air)
        # Base: AQI 90 -> 2, Temp 32°C -> +0 = 2. Multipliers: 1.3 * 1.1 * 1.0 = 1.43.
        # Score = 2 * 1.43 = 2.86 (Moderate)
        p4 = calculate_exposure(90, 31, 32, "18-30", "pregnant", "student")
        self.assertEqual(p4["score"], 2.86)
        self.assertEqual(p4["label"], LABEL_MODERATE)

        # Profile 5: Middle-Aged Elderly Caregiver with 'Other' condition
        # Base: AQI 180 -> 4, Temp 28°C -> +0 = 4. Multipliers: 1.2 * 1.15 * 1.2 = 1.656.
        # Score = 4 * 1.656 = 6.624 -> 6.62 (High)
        p5 = calculate_exposure(180, 110, 28, "51-65", "other", "elderly_caregiver")
        self.assertEqual(p5["score"], 6.62)
        self.assertEqual(p5["label"], LABEL_HIGH)

    def test_aqi_boundary_thresholds(self):
        """Verifies exact base risk values for all AQI boundaries."""
        # 0–50 -> base 1
        self.assertEqual(calculate_base_risk(aqi=0, temp=25)[0], 1)
        self.assertEqual(calculate_base_risk(aqi=50, temp=25)[0], 1)
        # 51–100 -> base 2
        self.assertEqual(calculate_base_risk(aqi=51, temp=25)[0], 2)
        self.assertEqual(calculate_base_risk(aqi=100, temp=25)[0], 2)
        # 101–150 -> base 3
        self.assertEqual(calculate_base_risk(aqi=101, temp=25)[0], 3)
        self.assertEqual(calculate_base_risk(aqi=150, temp=25)[0], 3)
        # 151–200 -> base 4
        self.assertEqual(calculate_base_risk(aqi=151, temp=25)[0], 4)
        self.assertEqual(calculate_base_risk(aqi=200, temp=25)[0], 4)
        # 201+ -> base 5
        self.assertEqual(calculate_base_risk(aqi=201, temp=25)[0], 5)
        self.assertEqual(calculate_base_risk(aqi=450, temp=25)[0], 5)

    def test_heat_compounding_boundary(self):
        """Verifies heat compounding adds +1 strictly when temp > 35°C."""
        # Temp exactly 35.0 -> no addition
        base_35, meta_35 = calculate_base_risk(aqi=120, temp=35.0)
        self.assertEqual(base_35, 3)
        self.assertFalse(meta_35["heat_compounded"])

        # Temp 35.1 -> compounds by +1
        base_351, meta_351 = calculate_base_risk(aqi=120, temp=35.1)
        self.assertEqual(base_351, 4)
        self.assertTrue(meta_351["heat_compounded"])

    def test_score_bucketing_boundaries(self):
        """Verifies score labels at exact boundary transitions."""
        self.assertEqual(bucket_score(0.0), LABEL_LOW)
        self.assertEqual(bucket_score(2.5), LABEL_LOW)
        self.assertEqual(bucket_score(2.51), LABEL_MODERATE)
        self.assertEqual(bucket_score(5.0), LABEL_MODERATE)
        self.assertEqual(bucket_score(5.01), LABEL_HIGH)
        self.assertEqual(bucket_score(8.0), LABEL_HIGH)
        self.assertEqual(bucket_score(8.01), LABEL_VERY_HIGH)
        self.assertEqual(bucket_score(15.0), LABEL_VERY_HIGH)

    def test_input_normalization_and_aliases(self):
        """Verifies case insensitivity, spaces, and synonyms."""
        res = calculate_exposure(
            aqi=100,
            temp=25,
            age_group="65 plus",
            health_condition="HEART CONDITION",
            occupation="Outdoor Worker",
        )
        self.assertEqual(res["breakdown"]["age_multiplier"], 1.35)
        self.assertEqual(res["breakdown"]["condition_multiplier"], 1.5)
        self.assertEqual(res["breakdown"]["occupation_multiplier"], 1.5)

    def test_fallback_aqi_from_pm25(self):
        """Verifies EPA PM2.5 calculation fallback when AQI is omitted."""
        # PM2.5 = 35.4 -> AQI ~ 100 -> base 2
        base_calc, meta = calculate_base_risk(aqi=None, pm25=35.4, temp=20)
        self.assertEqual(base_calc, 2)
        self.assertAlmostEqual(meta["effective_aqi"], 100.0, delta=1.0)


class TestSlidingWindowAlgorithm(unittest.TestCase):

    def test_sliding_window_finds_minimum(self):
        """
        Creates a 24-hour AQI profile with a known minimum at 19:00 - 21:00 (7 PM - 9 PM)
        and verifies that Section 9 sliding window algorithm identifies it correctly.
        """
        times = [f"2026-09-04T{h:02d}:00" for h in range(24)]
        # Make daytime high AQI (140-180), late evening low AQI (35-40 at hours 19 and 20)
        aqis = [150] * 24
        aqis[19] = 35  # 7 PM
        aqis[20] = 40  # 8 PM

        hourly_payload = {
            "time": times,
            "us_aqi": aqis,
            "pm2_5": [50] * 24,
            "temperature_2m": [30] * 24,
        }

        window_res = find_best_window(
            hourly_data=hourly_payload,
            age_group="18-30",
            health_condition="none",
            occupation="desk_job",
            window_hours=2,
        )

        self.assertEqual(window_res["best_window"], "7 PM – 9 PM")
        self.assertEqual(window_res["window_24h"], "19:00 – 21:00")
        self.assertEqual(window_res["start_hour"], 19)
        self.assertEqual(window_res["end_hour"], 21)
        self.assertEqual(window_res["label"], LABEL_LOW)
        self.assertEqual(len(window_res["hourly_scores"]), 24)

    def test_sliding_window_list_format(self):
        """Verifies list-of-dicts input format."""
        records = [
            {"time": f"2026-09-04T{h:02d}:00", "aqi": 150 if h != 6 and h != 7 else 30, "temp": 24}
            for h in range(24)
        ]
        window_res = find_best_window(records, "18-30", "none", "desk_job")
        self.assertEqual(window_res["best_window"], "6 AM – 8 AM")


if __name__ == "__main__":
    unittest.main()
