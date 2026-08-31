from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3604_rayjoin_pip_boundary_event_signal_timing_2026-06-06.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3604_rayjoin_pip_boundary_event_signal_timing_a5000" / "summary.json"
SCRIPT = ROOT / "scripts" / "goal3604_rayjoin_pip_boundary_event_signal_timing.py"
FUTURE_TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal3604RayJoinPipBoundaryEventSignalTimingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.future_todo = FUTURE_TODO.read_text(encoding="utf-8")

    def test_artifact_records_clean_tracked_runner_and_three_scale_packet(self):
        payload = self.artifact
        self.assertEqual(payload["schema"], "rtdl.goal3604.rayjoin_pip_boundary_event_signal_timing.v1")
        self.assertEqual(payload["goal"], 3604)
        self.assertEqual(payload["git_commit"], "7524cd565211f7e295d5f79a7028a63f7684ff84")
        self.assertEqual(payload["counts"], [512, 1024, 2048])
        self.assertEqual(payload["repeat"], 20)
        self.assertEqual(payload["warmup"], 5)
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertNotIn("scripts/goal3604_rayjoin_pip_boundary_event_signal_timing.py", payload["git_status_short"])

    def test_counts_match_exact_but_boundary_event_signal_is_not_performance_ready(self):
        payload = self.artifact
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertTrue(payload["summary"]["all_boundary_event_signal_counts_match_exact"])
        self.assertLess(payload["summary"]["geomean_boundary_event_signal_speedup_vs_cupy"], 0.05)
        self.assertLess(payload["summary"]["min_boundary_event_signal_speedup_vs_cupy"], 0.03)
        for row in payload["rows"]:
            with self.subTest(chain_count=row["chain_count"]):
                count = int(row["cupy_dense_cuda_core"]["row_count"])
                self.assertEqual(count, int(row["prepared_optix_exact"]["row_count"]))
                self.assertEqual(count, int(row["boundary_event_signal_route"]["filtered_row_count"]))
                self.assertTrue(row["boundary_event_signal_route"]["counts_match_exact"])
                self.assertGreater(row["boundary_event_signal_route"]["boundary_event_row_count"], row["boundary_event_signal_route"]["candidate_row_count"])
                self.assertLess(row["boundary_event_signal_speedup_vs_cupy"], 0.04)

    def test_report_keeps_route_selection_and_claim_boundary_honest(self):
        self.assertIn("not a performance route today", self.report)
        self.assertIn("recommend the CuPy dense CUDA-core scalar count", self.report)
        self.assertIn("best no-partner RTDL/OptiX PIP count route", self.report)
        self.assertIn("does not authorize", self.report)
        for key, value in self.artifact["claim_boundary"].items():
            self.assertFalse(value, key)

    def test_script_uses_generic_device_columns_and_safe_pair_key_range(self):
        self.assertIn("candidate_device_columns(points)", self.script)
        self.assertIn("first_boundary_crossing_device_columns", self.script)
        self.assertIn("run_selective_closed_shape_boundary_event_membership_pipeline_cupy", self.script)
        self.assertIn("combined_points = cp.concatenate((candidate_point_ids, zero_points))", self.script)
        self.assertIn("combined_shapes = cp.concatenate((candidate_shape_ids, zero_shapes))", self.script)

    def test_future_todo_captures_fused_closed_shape_count_lesson(self):
        self.assertIn("Goal3604", self.future_todo)
        self.assertIn("fuse exact closed-shape membership/count", self.future_todo)
        self.assertIn("not RayJoin paper reproduction", self.future_todo)


if __name__ == "__main__":
    unittest.main()
