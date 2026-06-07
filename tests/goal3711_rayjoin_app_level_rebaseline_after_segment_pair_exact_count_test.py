import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3711_rayjoin_app_level_rebaseline_after_segment_pair_exact_count_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3711_rayjoin_app_level_rebaseline_a5000" / "summary.json"


class Goal3711RayJoinAppLevelRebaselineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.row = cls.payload["rows"][0]
        cls.workloads = {entry["workload"]: entry for entry in cls.row["workloads"]}

    def test_artifact_is_current_main_a5000_rebaseline(self):
        self.assertEqual(self.payload["git_commit"], "4129ca8f912c3ad197c3c70a27c8bea0b4327456")
        self.assertIn("NVIDIA RTX A5000", self.payload["gpu"])
        self.assertEqual(self.payload["counts"], [4096])
        self.assertEqual(self.payload["repeat"], 20)
        self.assertTrue(self.row["all_counts_match"])
        self.assertAlmostEqual(self.row["all_cupy_sum_median_sec"], 1.4308710056357086)
        self.assertAlmostEqual(self.row["recommended_safe_mixed_sum_median_sec"], 0.005847812630236149)
        self.assertGreater(self.row["recommended_safe_mixed_speedup_vs_all_cupy"], 240.0)

    def test_subcontract_rows_record_current_routes_and_counts(self):
        pip = self.workloads["pip"]
        lsi = self.workloads["lsi"]
        overlay = self.workloads["overlay_seed"]

        self.assertEqual(pip["recommended_route_kind"], "cupy_dense_cuda_core")
        self.assertEqual(pip["recommended_route"]["row_count"], 11316)
        self.assertAlmostEqual(pip["recommended_speedup_vs_cupy"], 1.0)

        self.assertEqual(lsi["recommended_route_kind"], "rtdl_optix_exact_refined_count")
        self.assertEqual(lsi["recommended_route"]["row_count"], 4977)
        self.assertGreater(lsi["recommended_speedup_vs_cupy"], 8000.0)
        native = lsi["recommended_route"]["native_phase_timings"]
        self.assertEqual(native["mode"], "count_prepared_left")
        self.assertEqual(native["raw_candidate_count"], 5012)
        self.assertEqual(native["emitted_count"], 4977)
        self.assertEqual(native["candidate_download"], 0.0)
        self.assertEqual(native["exact_refine"], 0.0)
        self.assertEqual(native["left_upload"], 0.0)

        self.assertEqual(overlay["recommended_route_kind"], "rtdl_optix_active_count")
        self.assertEqual(overlay["recommended_route"]["row_count"], 4250)
        self.assertGreater(overlay["recommended_speedup_vs_cupy"], 30.0)

    def test_report_describes_comparison_scope_without_overclaiming(self):
        self.assertIn("same-contract benchmark evidence", self.report)
        self.assertIn("not a RayJoin paper reproduction", self.report)
        self.assertIn("not an RTDL-beats-RayJoin claim", self.report)
        self.assertIn("all-CuPy dense same-contract baseline", self.report)
        self.assertIn("Compare this app-level mixed route against the original RayJoin implementation", self.report)
        self.assertIn("PIP is exactly parity with CuPy because the recommended route is still CuPy", self.report)

    def test_claim_boundary_flags_remain_false(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        for workload in self.row["workloads"]:
            for key, value in workload["claim_boundary"].items():
                self.assertFalse(value, f"{workload['workload']}:{key}")
            for key, value in workload["recommended_route"]["claim_boundary"].items():
                if key == "internal_results_only":
                    self.assertTrue(value)
                else:
                    self.assertFalse(value, f"{workload['workload']} recommended:{key}")


if __name__ == "__main__":
    unittest.main()
