import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3713_rayjoin_native_pip_current_composite_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3713_rayjoin_native_pip_current_composite_a5000" / "summary.json"


class Goal3713RayJoinNativePipCurrentCompositeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.row = cls.payload["rows"][0]
        cls.workloads = {entry["workload"]: entry for entry in cls.row["workloads"]}

    def test_artifact_is_current_main_native_pip_packet(self):
        self.assertEqual(self.payload["git_commit"], "7cf5e2f37e4576a1d3a51d670fcde05cb79d310d")
        self.assertIn("NVIDIA RTX A5000", self.payload["gpu"])
        self.assertEqual(self.payload["counts"], [4096])
        self.assertEqual(self.payload["repeat"], 20)
        self.assertTrue(self.payload["summary"]["all_counts_match"])
        self.assertTrue(self.row["all_counts_match"])
        self.assertAlmostEqual(self.row["all_cupy_sum_median_sec"], 1.4307143362239003)
        self.assertAlmostEqual(self.row["native_pip_safe_mixed_sum_median_sec"], 0.0053226398304104805)
        self.assertGreater(self.row["native_pip_safe_mixed_speedup_vs_all_cupy"], 260.0)

    def test_native_pip_route_replaces_cupy_pip_leg(self):
        pip = self.workloads["pip"]
        self.assertEqual(pip["candidate_route_kind"], "rtdl_optix_native_scalar_count_executor")
        self.assertEqual(pip["candidate_route"]["execution_route"], "prepared_native_relation_status_corrected_scalar_count_executor")
        self.assertEqual(pip["candidate_route"]["row_count"], 11316)
        self.assertGreater(pip["candidate_speedup_vs_cupy"], 2.5)
        self.assertFalse(pip["candidate_route"]["row_stream_materialized"])
        self.assertFalse(pip["candidate_route"]["boundary_candidate_row_stream_materialized"])

    def test_lsi_and_overlay_remain_current_rtdl_routes(self):
        lsi = self.workloads["lsi"]
        overlay = self.workloads["overlay_seed"]

        self.assertEqual(lsi["candidate_route_kind"], "rtdl_optix_exact_refined_count")
        self.assertEqual(lsi["candidate_route"]["row_count"], 4977)
        self.assertGreater(lsi["candidate_speedup_vs_cupy"], 7000.0)
        self.assertTrue(lsi["candidate_route"].get("prepared_left_for_count"))
        native = lsi["candidate_route"].get("native_phase_timings", {})
        self.assertEqual(native.get("mode"), "count_prepared_left")
        self.assertEqual(native.get("candidate_download"), 0.0)
        self.assertEqual(native.get("exact_refine"), 0.0)

        self.assertEqual(overlay["candidate_route_kind"], "rtdl_optix_active_count")
        self.assertEqual(overlay["candidate_route"]["row_count"], 4250)
        self.assertGreater(overlay["candidate_speedup_vs_cupy"], 30.0)

    def test_report_compares_to_goal3711_and_preserves_boundary(self):
        self.assertIn("Goal3711", self.report)
        self.assertIn("Goal3713", self.report)
        self.assertIn("`1.099x` improvement in the mixed composite", self.report)
        self.assertIn("`2.590x` improvement on the PIP leg alone", self.report)
        self.assertIn("pending external review", self.report)
        self.assertIn("not a public speedup claim", self.report)
        self.assertIn("not an RTDL-beats-RayJoin claim", self.report)

    def test_claim_boundary_flags_remain_false(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        for workload in self.row["workloads"]:
            for key, value in workload["claim_boundary"].items():
                self.assertFalse(value, f"{workload['workload']}:{key}")
            for key, value in workload["candidate_route"]["claim_boundary"].items():
                if key == "internal_results_only":
                    self.assertTrue(value)
                else:
                    self.assertFalse(value, f"{workload['workload']} candidate:{key}")


if __name__ == "__main__":
    unittest.main()
