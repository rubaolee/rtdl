import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal2270_prepared_segment_pair_count_probe_pod_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2270_prepared_segment_pair_count_probe_2026-05-17.md"


class Goal2270PreparedSegmentPairCountProbeTest(unittest.TestCase):
    def test_pod_artifact_records_clean_commit_and_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["goal"], 2270)
        self.assertEqual(payload["commit"], "dffabc1317f382dcb19cd3ea30087692a0b69e48")
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rayjoin_paper_dataset_claim_authorized"])
        self.assertIn("same OptiX custom primitive traversal path", payload["claim_boundary"]["rt_core_claim"])

    def test_counts_match_raw_rows_at_all_scales(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        results = payload["results"]

        self.assertGreaterEqual(len(results), 6)
        for row in results:
            self.assertTrue(row["parity"], row)
            self.assertEqual(row["raw_row_count"], row["expected_intersections"])
            self.assertEqual(row["scalar_count"], row["expected_intersections"])

    def test_larger_scales_show_count_surface_benefit(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        large_rows = [row for row in payload["results"] if row["expected_intersections"] >= 589_824]

        self.assertGreaterEqual(len(large_rows), 4)
        self.assertTrue(all(row["count_to_row_ratio"] < 1.0 for row in large_rows), large_rows)
        self.assertGreaterEqual(max(row["row_to_count_speedup"] for row in large_rows), 1.3)

    def test_report_keeps_claims_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("not a whole RayJoin application claim", text)
        self.assertIn("not a RayJoin paper dataset claim", text)
        self.assertIn("not automatically faster at tiny scales", text)
        self.assertIn("future version needs a device-resident", text)


if __name__ == "__main__":
    unittest.main()
