import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3654_rayjoin_lsi_10s_prepared_left_long_run_2026-06-06.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3654_rayjoin_lsi_10s_prepared_left_a5000"
    / "lsi_4096_10s_summary.json"
)


class Goal3654RayJoinLsi10sPreparedLeftLongRunTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_lsi_only_long_run_matches_visible_count(self):
        self.assertEqual(self.artifact["rtdl_commit"][:8], "e32d0f3e")
        self.assertEqual(self.artifact["selected_workloads"], ["lsi"])
        lsi = self.artifact["comparisons"][0]
        self.assertEqual(lsi["workload"], "lsi")
        self.assertEqual(lsi["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(lsi["rayjoin_visible_count"], 4977)
        self.assertEqual(lsi["rtdl_count"], 4977)

    def test_long_run_records_ten_second_class_totals(self):
        rayjoin = self.artifact["rayjoin"]["lsi"]
        rtdl = self.artifact["rtdl"]["lsi"]
        self.assertEqual(rayjoin["process_wall_ms"]["count"], 3)
        self.assertGreater(rayjoin["process_wall_ms"]["median"], 10_000.0)
        self.assertEqual(rtdl["prepared_query_total_ms"]["count"], 3)
        self.assertGreater(rtdl["prepared_query_total_ms"]["median"], 10_000.0)
        self.assertEqual(rtdl["internal_query_repeat"], 100000)
        self.assertEqual(rtdl["internal_warmup"], 100)

    def test_lsi_prepared_left_query_ratio_is_stronger_than_short_packet(self):
        lsi = self.artifact["comparisons"][0]
        self.assertLess(lsi["rtdl_over_rayjoin_query_ratio"], 0.3)
        self.assertLess(lsi["rtdl_prepared_query_ms_median"], lsi["rayjoin_query_ms_reported_median"])

    def test_claim_boundaries_are_still_blocked(self):
        self.assertEqual(self.artifact["status"], "pass_with_optimization_gap")
        for flag, value in self.artifact["claim_boundary"].items():
            self.assertFalse(value, flag)
        self.assertIn("does not authorize", self.report)
        self.assertIn("full RayJoin paper reproduction claims", self.report)
        self.assertIn("PIP, overlay, or full RayJoin", self.report)


if __name__ == "__main__":
    unittest.main()
