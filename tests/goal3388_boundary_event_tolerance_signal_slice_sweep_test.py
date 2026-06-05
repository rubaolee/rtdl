from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3388_boundary_event_tolerance_signal_slice_sweep_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3388_boundary_event_tolerance_signal_slice_sweep_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3388_boundary_event_tolerance_signal_slice_sweep.py"


class Goal3388BoundaryEventToleranceSignalSliceSweepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_artifact_uses_live_optix_columns_and_oracle_only_for_evaluation(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3388.boundary_event_tolerance_signal_slice_sweep.v1")
        self.assertEqual(payload["goal"], 3388)
        self.assertEqual(payload["counts"], [512, 1024, 2048])
        self.assertEqual(payload["start"], 256)
        self.assertAlmostEqual(payload["crossing_tolerance"], 1e-5)
        self.assertTrue(payload["candidate_rows_from_optix_device_columns"])
        self.assertTrue(payload["boundary_rows_from_optix_device_columns"])
        self.assertTrue(payload["exact_oracle_generated_by_live_optix_run"])
        self.assertTrue(payload["exact_oracle_used_only_for_signal_evaluation"])
        self.assertTrue(payload["signal_inputs_exclude_exact_oracle"])
        self.assertIn("candidate_device_columns(points)", self.script)
        self.assertIn("first_boundary_crossing_device_columns", self.script)
        self.assertIn("prepared.run(points)", self.script)
        self.assertNotIn("selected_point_ids = [522", self.script)

    def test_all_three_slices_match_exact_after_tolerance_filter(self):
        payload = self.payload
        self.assertTrue(payload["all_rows_match_exact"])
        self.assertTrue(payload["all_boundary_outputs_device_resident"])
        self.assertFalse(payload["any_boundary_overflow"])
        rows = {row["point_count"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {512, 1024, 2048})

        expected = {
            512: {
                "candidate": 1429,
                "boundary": 4836,
                "exact": 1417,
                "extras": 12,
                "selected": 10,
                "dropped": 12,
            },
            1024: {
                "candidate": 2844,
                "boundary": 16173,
                "exact": 2827,
                "extras": 17,
                "selected": 15,
                "dropped": 17,
            },
            2048: {
                "candidate": 5672,
                "boundary": 34133,
                "exact": 5619,
                "extras": 53,
                "selected": 40,
                "dropped": 53,
            },
        }
        for point_count, row in rows.items():
            with self.subTest(point_count=point_count):
                pinned = expected[point_count]
                self.assertEqual(row["optix_candidate_row_count"], pinned["candidate"])
                self.assertEqual(row["boundary_event_row_count"], pinned["boundary"])
                self.assertEqual(row["exact_row_count"], pinned["exact"])
                self.assertEqual(row["candidate_extra_row_count_before_filter"], pinned["extras"])
                self.assertEqual(row["selected_point_count"], pinned["selected"])
                self.assertEqual(row["selected_dropped_row_count"], pinned["dropped"])
                self.assertEqual(row["filtered_row_count"], pinned["exact"])
                self.assertTrue(row["matches_exact"])
                self.assertEqual(row["missing_exact_row_count"], 0)
                self.assertEqual(row["extra_row_count"], 0)

    def test_signal_is_bounded_over_selection_not_oracle_selection(self):
        for row in self.payload["rows"]:
            self.assertEqual(row["selected_false_positive_point_ids"], [633, 634, 635])
            self.assertEqual(row["selected_missed_extra_point_ids"], [])
            self.assertGreaterEqual(row["selected_point_count"], row["true_extra_point_count"])
            self.assertEqual(
                row["candidate_extra_row_count_before_filter"],
                row["selected_dropped_row_count"],
            )
        self.assertEqual(
            self.payload["selected_point_signal"],
            "candidate_count_gt_strict_zero_boundary_candidate_count_and_strict_zero_count_lte_2",
        )
        self.assertEqual(
            self.payload["filter"],
            "selected_candidate_pair_has_boundary_crossing_t_within_tolerance",
        )

    def test_claim_boundaries_and_report_remain_bounded(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertIn("does not authorize a native default route", self.report)
        self.assertIn("does not authorize release", self.report)
        self.assertIn("not only `br_county`", self.report)


if __name__ == "__main__":
    unittest.main()
