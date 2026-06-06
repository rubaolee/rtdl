import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3646_prepared_segment_left_set_amortized_sparse_probe_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3646_segment_pair_prepared_left_amortized_a5000" / "summary.json"


class Goal3646PreparedSegmentLeftSetAmortizedSparseProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_amortized_artifact_is_clean_and_correct(self):
        self.assertEqual(self.summary["git_commit"][:8], "6e061d83")
        self.assertEqual(self.summary["git_tracked_status_short"], "")
        self.assertTrue(self.summary["warmup"]["cupy_rawkernel_warmed"])
        self.assertTrue(self.summary["warmup"]["optix_pipeline_warmed"])
        self.assertTrue(self.summary["all_same_contract_source_counts_match"])
        self.assertEqual(len(self.summary["cases"]), 3)
        for case in self.summary["cases"]:
            size = int(case["name"].rsplit("_", 1)[1])
            self.assertEqual(case["left_count"], size)
            self.assertEqual(case["right_count"], size)
            self.assertEqual(case["candidate_pair_count"], size * size)
            self.assertEqual(case["expected_hit_pair_count"], size)
            self.assertEqual(case["repetitions"], 200)

    def test_repeated_prepared_left_hot_route_ratios_are_visible(self):
        ratios = {
            case["name"]: case["cupy_kernel_over_prepared_left_mean"]
            for case in self.summary["cases"]
        }
        amortized = {
            case["name"]: case["cupy_kernel_over_prepared_left_mean_with_amortized_prepare"]
            for case in self.summary["cases"]
        }
        self.assertGreater(ratios["sparse_diagonal_grid_8192"], 100.0)
        self.assertGreater(ratios["sparse_diagonal_grid_16384"], 400.0)
        self.assertGreater(ratios["sparse_diagonal_grid_32768"], 1500.0)
        self.assertGreater(amortized["sparse_diagonal_grid_8192"], 50.0)
        self.assertGreater(amortized["sparse_diagonal_grid_16384"], 100.0)
        self.assertGreater(amortized["sparse_diagonal_grid_32768"], 300.0)

    def test_report_keeps_hot_route_boundary_explicit(self):
        self.assertIn("hot-route probe", self.report)
        self.assertIn("not a one-shot app-wall benchmark", self.report)
        self.assertIn("does not authorize", self.report)
        self.assertIn("preparation cost explicitly reported and amortized", self.report)
        for flag, value in self.summary["claim_boundary"].items():
            self.assertFalse(value, flag)


if __name__ == "__main__":
    unittest.main()
