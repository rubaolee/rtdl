import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3725_rayjoin_lsi_grouped_range_policy_sweep_2026-06-07.md"
CONFIRM = ROOT / "docs" / "reports" / "goal3724_rayjoin_lsi_grouped_range_route_confirm_a5000" / "summary.json"
BEST = ROOT / "docs" / "reports" / "goal3724_rayjoin_lsi_grouped_range_route_confirm_a5000" / "max1_area1.5.json"
SWEEP = ROOT / "docs" / "reports" / "goal3724_rayjoin_lsi_grouped_range_route_sweep_a5000" / "summary.json"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3725RayJoinLsiGroupedRangePolicySweepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.confirm = json.loads(CONFIRM.read_text(encoding="utf-8"))
        cls.best_artifact = json.loads(BEST.read_text(encoding="utf-8"))
        cls.sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
        cls.workloads = WORKLOADS.read_text(encoding="utf-8")

    def test_best_confirmed_policy_is_identity_range_and_correct(self):
        best = self.confirm["best"]
        comparison = self.best_artifact["comparison"]
        self.assertEqual(1, int(best["policy"]["max_size"]))
        self.assertEqual(1.5, float(best["policy"]["area_enlarge"]))
        self.assertEqual(326193, int(best["group_count"]))
        self.assertEqual(326193, int(comparison["right_segment_count"]))
        self.assertTrue(best["counts_match"])
        self.assertTrue(comparison["counts_match"])
        self.assertEqual(20860, int(comparison["rayjoin_lsi_intersections"]))
        self.assertEqual(20860, int(comparison["rtdl_count"]))

    def test_best_policy_is_materially_faster_on_measured_contract(self):
        best = self.confirm["best"]
        self.assertLess(float(best["grouped_sec"]), float(best["rayjoin_sec"]))
        self.assertLess(float(best["grouped_sec"]), float(best["existing_sec"]))
        self.assertGreater(float(best["speedup_vs_rayjoin"]), 3.0)
        self.assertGreater(float(best["speedup_vs_existing"]), 5.0)
        self.assertIn("3.215x vs RayJoin", self.report)
        self.assertIn("5.290x vs existing RTDL any-hit", self.report)

    def test_policy_sweep_records_over_grouping_failure_mode(self):
        rows = self.sweep["rows"]
        slow_rows = [
            row for row in rows
            if int(row["policy"]["max_size"]) >= 32 and float(row["policy"]["area_enlarge"]) >= 2.0
        ]
        self.assertTrue(slow_rows)
        self.assertTrue(any(float(row["speedup_vs_existing"]) < 1.0 for row in slow_rows))
        self.assertIn("Too much grouping lowers BVH primitive count", self.report)
        self.assertIn("enlarges primitive boxes", self.report)

    def test_diagnostic_route_default_matches_measured_safe_policy(self):
        self.assertIn("size_t max_segments_per_group = 1;", self.workloads)
        self.assertIn("float area_enlarge_limit = 1.5f;", self.workloads)
        self.assertIn("environment overrides", self.report)
        self.assertIn("does not promote this diagnostic route as a public default route", self.report)

    def test_claim_boundary_remains_non_authorizing(self):
        boundary = self.best_artifact["claim_boundary"]
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "native_default_route_authorized",
        ):
            self.assertFalse(boundary[key], key)
        self.assertIn("This goal does not authorize", self.report)
        self.assertIn("diagnostic single-contract A5000 measurement", self.report)


if __name__ == "__main__":
    unittest.main()
