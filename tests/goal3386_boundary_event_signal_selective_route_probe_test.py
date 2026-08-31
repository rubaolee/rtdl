from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3386_boundary_event_signal_selective_route_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3386_boundary_event_signal_selective_route_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3386_boundary_event_signal_selective_route_probe.py"


class Goal3386BoundaryEventSignalSelectiveRouteProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_probe_uses_live_candidate_and_boundary_device_columns(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3386.boundary_event_signal_selective_route_probe.v1")
        self.assertEqual(payload["goal"], 3386)
        self.assertTrue(payload["candidate_rows_from_optix_device_columns"])
        self.assertTrue(payload["boundary_rows_from_optix_device_columns"])
        self.assertTrue(payload["boundary_event_device_resident"])
        self.assertFalse(payload["boundary_event_overflow"])
        self.assertTrue(payload["signal_inputs_exclude_exact_oracle"])
        self.assertTrue(payload["exact_oracle_used_only_for_signal_evaluation"])
        self.assertIn("candidate_device_columns(points)", self.script)
        self.assertIn("first_boundary_crossing_device_columns", self.script)
        self.assertIn("prepared.run(points)", self.script)

    def test_signal_selects_exactly_true_candidate_extra_points(self):
        payload = self.payload
        self.assertEqual(payload["selected_point_ids"], [522, 523, 538, 539, 540, 564, 565])
        self.assertEqual(payload["true_extra_point_ids"], [522, 523, 538, 539, 540, 564, 565])
        self.assertTrue(payload["selected_points_match_true_extra_points"])
        self.assertIn("zero_count_eq2", payload["selected_point_signal"])
        self.assertEqual(len(payload["selected_feature_rows"]), 7)
        for row in payload["selected_feature_rows"]:
            self.assertEqual(row["zero_boundary_candidate_count"], 2)
            self.assertEqual(row["incident_row_count"], 3)
            self.assertEqual(row["candidate_face_count"], 4)

    def test_selective_boundary_event_filter_matches_live_exact(self):
        payload = self.payload
        self.assertEqual(payload["optix_candidate_row_count"], 1429)
        self.assertEqual(payload["boundary_event_row_count"], 4836)
        self.assertEqual(payload["exact_row_count"], 1417)
        self.assertEqual(payload["candidate_extra_row_count_before_filter"], 12)
        self.assertEqual(payload["selected_candidate_row_count"], 26)
        self.assertEqual(payload["selected_kept_row_count"], 14)
        self.assertEqual(payload["selected_dropped_row_count"], 12)
        self.assertEqual(payload["passthrough_candidate_row_count"], 1403)
        self.assertEqual(payload["filtered_row_count"], 1417)
        self.assertTrue(payload["matches_exact"])
        self.assertEqual(payload["missing_exact_row_count"], 0)
        self.assertEqual(payload["extra_row_count"], 0)
        self.assertEqual(payload["boundary_event_filter"], "candidate_pair_has_zero_crossing_t")

    def test_claim_boundaries_stay_blocked_and_report_is_bounded(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertIn("not yet a default route", self.report)
        self.assertIn("one bounded", self.report)
        self.assertIn("claim-boundary flags remain false", self.report)


if __name__ == "__main__":
    unittest.main()
