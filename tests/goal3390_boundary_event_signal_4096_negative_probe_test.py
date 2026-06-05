from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3390_boundary_event_signal_4096_negative_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3390_boundary_event_signal_4096_negative_probe_2026-06-04.md"


class Goal3390BoundaryEventSignal4096NegativeProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.row = cls.payload["rows"][0]

    def test_4096_probe_is_a_real_live_device_column_negative(self):
        self.assertEqual(self.payload["schema"], "rtdl.goal3388.boundary_event_tolerance_signal_slice_sweep.v1")
        self.assertEqual(self.payload["counts"], [4096])
        self.assertEqual(self.row["point_count"], 4096)
        self.assertEqual(self.row["shape_count"], 3762)
        self.assertTrue(self.payload["candidate_rows_from_optix_device_columns"])
        self.assertTrue(self.payload["boundary_rows_from_optix_device_columns"])
        self.assertTrue(self.payload["exact_oracle_generated_by_live_optix_run"])
        self.assertTrue(self.payload["exact_oracle_used_only_for_signal_evaluation"])
        self.assertTrue(self.payload["signal_inputs_exclude_exact_oracle"])
        self.assertTrue(self.row["boundary_event_device_resident"])
        self.assertFalse(self.row["boundary_event_overflow"])

    def test_current_tolerance_signal_fails_at_4096(self):
        row = self.row
        self.assertFalse(self.payload["all_rows_match_exact"])
        self.assertFalse(row["matches_exact"])
        self.assertEqual(row["optix_candidate_row_count"], 11431)
        self.assertEqual(row["boundary_event_row_count"], 70458)
        self.assertEqual(row["exact_row_count"], 11316)
        self.assertEqual(row["candidate_extra_row_count_before_filter"], 115)
        self.assertEqual(row["selected_point_count"], 103)
        self.assertEqual(row["selected_candidate_row_count"], 306)
        self.assertEqual(row["selected_dropped_row_count"], 117)
        self.assertEqual(row["filtered_row_count"], 11314)
        self.assertEqual(row["missing_exact_row_count"], 3)
        self.assertEqual(row["extra_row_count"], 1)
        self.assertEqual(
            row["missing_sample"],
            [[4283, 4286], [4284, 4286], [4285, 4286]],
        )
        self.assertEqual(row["extra_sample"], [[3738, 3829]])
        self.assertEqual(row["selected_missed_extra_point_ids"], [3738])
        self.assertIn(4283, row["selected_false_positive_point_ids"])

    def test_report_blocks_route_promotion_and_names_generic_gap(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertIn("blocks route promotion", self.report)
        self.assertIn("first-boundary-event stream is not rich enough", self.report)
        self.assertIn("exact, device-resident closed-shape relation stream", self.report)
        self.assertIn("no RayJoin, CDB, county, owner-face", self.report)


if __name__ == "__main__":
    unittest.main()
