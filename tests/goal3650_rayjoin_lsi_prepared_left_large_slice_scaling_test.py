import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3650_rayjoin_lsi_prepared_left_large_slice_scaling_2026-06-06.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3650_rayjoin_lsi_prepared_left_large_slice_a5000"
    / "same_slice_4096_summary.json"
)


class Goal3650RayJoinLsiPreparedLeftLargeSliceScalingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_large_slice_lsi_visible_count_matches(self):
        self.assertEqual(self.artifact["rtdl_commit"][:8], "13e40398")
        lsi = next(row for row in self.artifact["comparisons"] if row["workload"] == "lsi")
        self.assertEqual(lsi["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(lsi["rayjoin_visible_count"], 4977)
        self.assertEqual(lsi["rtdl_count"], 4977)

    def test_large_slice_lsi_prepared_query_is_faster_than_rayjoin_query_timing(self):
        lsi = next(row for row in self.artifact["comparisons"] if row["workload"] == "lsi")
        self.assertLess(lsi["rtdl_over_rayjoin_query_ratio"], 0.6)
        self.assertLess(lsi["rtdl_prepared_query_ms_median"], lsi["rayjoin_query_ms_reported_median"])
        self.assertGreater(
            lsi["rayjoin_query_ms_reported_median"] / lsi["rtdl_prepared_query_ms_median"],
            1.7,
        )

    def test_boundaries_block_overclaim(self):
        self.assertEqual(self.artifact["status"], "pass_with_optimization_gap")
        for flag, value in self.artifact["claim_boundary"].items():
            self.assertFalse(value, flag)
        self.assertIn("full RayJoin paper reproduction claims", self.report)
        self.assertIn("not authorize", self.report)
        self.assertIn("PIP, overlay, or full RayJoin", self.report)


if __name__ == "__main__":
    unittest.main()
