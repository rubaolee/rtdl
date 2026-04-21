import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal696_optix_fixed_radius_summary_linux_validation_2026-04-21.md"
DATA = ROOT / "docs" / "reports" / "goal696_optix_fixed_radius_summary_linux_validation_2026-04-21.json"
HANDOFF = ROOT / "docs" / "handoff" / "GOAL695_DEV_AI_OPTIX_REDESIGN_REQUEST_2026-04-21.md"


class Goal696OptixFixedRadiusLinuxValidationTest(unittest.TestCase):
    def test_linux_validation_report_preserves_honesty_boundaries(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "ACCEPT for native Linux build and correctness",
            "No performance-classification change",
            "GTX 1070 has no RT cores",
            "neighbor_row_count: 0",
            "15 tests OK",
            "Outlier detection and DBSCAN remain classified as `cuda_through_optix`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_linux_validation_json_records_no_classification_change(self):
        payload = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(payload["commit"], "c569e71")
        self.assertEqual(payload["build"]["result"], "pass")
        self.assertTrue(payload["direct_correctness"]["outlier_summary_matches_oracle"])
        self.assertTrue(payload["direct_correctness"]["dbscan_core_flags_match_oracle"])
        self.assertEqual(payload["direct_correctness"]["outlier_neighbor_rows_materialized"], 0)
        self.assertEqual(payload["direct_correctness"]["dbscan_neighbor_rows_materialized"], 0)
        self.assertFalse(payload["conclusion"]["classification_change"])

    def test_all_timing_cases_preserve_oracle_parity(self):
        payload = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(payload["timing"]["cases"]), 12)
        for case in payload["timing"]["cases"]:
            with self.subTest(label=case["label"]):
                self.assertTrue(case["matches_oracle"])
                self.assertGreater(case["median_sec"], 0.0)

    def test_dev_ai_handoff_does_not_reintroduce_overclaims(self):
        text = HANDOFF.read_text(encoding="utf-8")
        for phrase in (
            "GTX 1070, which has no RT cores",
            "Outlier detection and DBSCAN remain `cuda_through_optix`",
            "RT hardware does not enumerate misses",
            "Do not promote Hausdorff/KNN/Barnes-Hut",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertNotIn("RT Core automatically rejects the AABB, indicating the node is mathematically far enough", text)


if __name__ == "__main__":
    unittest.main()
