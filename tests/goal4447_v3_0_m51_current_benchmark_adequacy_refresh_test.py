from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4447_v3_0_m51_current_benchmark_adequacy_refresh_2026-06-16.md"


class Goal4447V30M51CurrentBenchmarkAdequacyRefreshTest(unittest.TestCase):
    def test_current_adequacy_refreshes_to_v3_without_authorizing_claims(self) -> None:
        validation = rt.validate_current_benchmark_adequacy()
        summary = rt.summarize_current_benchmark_adequacy()

        self.assertEqual(rt.CURRENT_BENCHMARK_ADEQUACY_VERSION, "rtdl.v3_0.current_benchmark_adequacy.goal4477.v1")
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["row_count"], 10)
        self.assertEqual(summary["adequacy_counts"]["strong"], 4)
        self.assertEqual(summary["adequacy_counts"]["adequate"], 6)
        self.assertEqual(summary["adequacy_counts"]["needs_major_followup"], 0)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["whole_app_speedup_claim_authorized"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertIn("Goal4450", summary["claim_boundary"])
        self.assertIn("Goal4451", summary["claim_boundary"])

    def test_v3_changed_rows_are_current(self) -> None:
        rows = {row["app"]: row for row in rt.current_benchmark_adequacy()}

        dbscan = rows["rt_dbscan"]
        self.assertIn("Goal4445", dbscan["evidence_refs"])
        self.assertIn('output_mode="component_signature"', dbscan["current_recommended_path"])
        self.assertIn("per-point Python cluster rows", dbscan["current_performance_reading"])

        robot = rows["robot_collision"]
        self.assertIn("Goal4446", robot["evidence_refs"])
        self.assertIn('lowering_mode="numpy_arrays"', robot["current_recommended_path"])
        self.assertIn("NumPy vectorized endpoint arrays", robot["current_performance_reading"])

        barnes = rows["barnes_hut"]
        self.assertEqual("adequate", barnes["adequacy"])
        self.assertIn("Goal4442", barnes["evidence_refs"])
        self.assertIn("Goal4448", barnes["evidence_refs"])
        self.assertIn("Goal4449", barnes["evidence_refs"])
        self.assertIn("Goal4450", barnes["evidence_refs"])
        self.assertIn("fused-subtree prototype", barnes["current_performance_reading"])
        self.assertIn("fused_frontier_force_sum_bucketized_numba_cuda", barnes["current_recommended_path"])
        self.assertIn("prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda", barnes["current_recommended_path"])
        self.assertIn("RT-native/device primitive", barnes["next_generic_runtime_action"])

        rayjoin = rows["spatial_rayjoin"]
        self.assertEqual("strong", rayjoin["adequacy"])
        self.assertIn("Goal4050", rayjoin["evidence_refs"])
        self.assertIn("Goal4451", rayjoin["evidence_refs"])
        self.assertIn("batch executor", rayjoin["current_recommended_path"])
        self.assertIn("fail-closes unsafe graph replay", rayjoin["next_generic_runtime_action"])

        rtnn = rows["rtnn"]
        self.assertEqual("strong", rtnn["adequacy"])
        self.assertIn("Goal4381", rtnn["evidence_refs"])
        self.assertIn("Goal4443", rtnn["evidence_refs"])
        self.assertIn("exact float64", rtnn["current_recommended_path"])
        self.assertIn("resident graph bridge", rtnn["current_performance_reading"])

        triangle = rows["triangle_counting"]
        self.assertIn("Goal4444", triangle["evidence_refs"])
        self.assertIn("Goal4461", triangle["evidence_refs"])
        self.assertIn("19.96x-23.07x", triangle["current_performance_reading"])
        self.assertIn("post-M78 comparison packet", triangle["next_generic_runtime_action"])

    def test_report_documents_overlay_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4447",
            "current API is no longer a v2.10 alias",
            "Barnes-Hut",
            "RT-DBSCAN",
            "Robot collision",
            "RTNN",
            "Triangle counting",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()


