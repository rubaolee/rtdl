from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3446_v2_8_runtime_gap_after_rayjoin_active_count_device_default_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3443_spatial_rayjoin_overlay_active_count_device_default_pod_2026-06-05.json"


class Goal3446V28RuntimeGapAfterRayJoinActiveCountDeviceDefaultTest(unittest.TestCase):
    def test_spatial_rayjoin_gap_row_records_device_active_count_default(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("generic device-side active-count continuation", spatial["current_best_path"])
        self.assertIn("default overlay scalar-summary route", spatial["current_best_path"])
        self.assertIn("Goal3441 showed the former host overlay active-count bottleneck", spatial["current_bottleneck"])
        self.assertIn("Goal3442/3443 moved the scalar active-count continuation onto the device", spatial["current_bottleneck"])
        self.assertIn("Remaining work is device-resident relation-row output for full overlay rows", spatial["current_bottleneck"])
        self.assertIn("richer parity/count grouping over resident row streams", spatial["current_bottleneck"])
        for goal in ("Goal3441", "Goal3442", "Goal3443"):
            with self.subTest(goal=goal):
                self.assertIn(goal, spatial["evidence_refs"])

    def test_gap_map_still_preserves_all_claim_boundaries(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()
        spatial = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}["spatial_rayjoin"]

        self.assertEqual(validation["status"], "accept", validation)
        for field in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(spatial[field])
                if field in validation:
                    self.assertFalse(validation[field])

    def test_report_records_solved_scalar_route_and_remaining_gap(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3446",
            "overlay scalar active count",
            "Goal3441 measured the old host route",
            "Goal3442 added a generic device-side active-count continuation",
            "Goal3443 promoted that device continuation",
            "remaining hard gap is not scalar count",
            "full overlay relation-row output",
            "app-specific native engine logic",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3443 pod artifact pending")
    def test_goal3443_artifact_records_device_default_shape(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        overlay = payload["routes"]["overlay_active_count"]

        self.assertEqual(overlay["row_counts"], [4543, 4543, 4543, 4543])
        self.assertEqual(
            overlay["last_native_phase_timings"]["mode"],
            "active_count_device_continuation",
        )
        self.assertIn("active_count_device_continuation_sec", overlay["runs"][-1]["phases_sec"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
