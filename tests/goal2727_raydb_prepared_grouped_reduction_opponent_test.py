import inspect
import json
import unittest
from pathlib import Path

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb
from scripts import goal2685_raydb_device_hit_stream_handoff_pod_runner as runner


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2727_raydb_prepared_grouped_reduction_opponent_2026-05-30.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2727_pod_artifacts"
    / "goal2727_raydb_prepared_grouped_vs_hit_stream_large_pod_69_30_85_171_2026-05-30.json"
)


class Goal2727RaydbPreparedGroupedReductionOpponentTest(unittest.TestCase):
    def test_prepared_grouped_reduction_backend_is_public_to_app_runner(self) -> None:
        self.assertEqual(
            raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND,
            "paper_rt_optix_prepared_grouped_reduction",
        )
        self.assertIn(raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND, raydb.BACKENDS)

    def test_backend_reuses_prepared_scene_payload_and_ray_batch(self) -> None:
        source = inspect.getsource(raydb._run_paper_rt_prepared_grouped_reduction_result_mode)

        self.assertIn("prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d", source)
        self.assertIn("prepared.prepare_ray_batch", source)
        self.assertIn("prepared.run_prepared_rays", source)
        self.assertIn("\"prepared_steady_state\": True", source)
        self.assertIn("\"prepared_primitive_payload_reused\": True", source)
        self.assertIn("\"prepared_optix_scene_reused\": True", source)
        self.assertIn("\"prepared_ray_batch_reused\": True", source)
        self.assertIn("\"native_device_column_path_used\": False", source)
        self.assertIn("\"host_row_bridge_bypassed\": False", source)
        self.assertIn("\"true_zero_copy_authorized\": False", source)

    def test_run_result_mode_dispatches_to_prepared_grouped_reduction(self) -> None:
        source = inspect.getsource(raydb.run_result_mode)

        self.assertIn("PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND", source)
        self.assertIn("_run_paper_rt_prepared_grouped_reduction_result_mode", source)
        self.assertIn("repeat=repeat", source)
        self.assertIn("warmup=warmup", source)

    def test_pod_runner_treats_both_prepared_paths_as_single_call_internal_repeat(self) -> None:
        source = inspect.getsource(runner._run_case)

        self.assertIn("prepared_backends", source)
        self.assertIn("PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND", source)
        self.assertIn("PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND", source)
        self.assertIn("prepared_iteration_wall_sec", source)

    def test_large_pod_artifact_records_negative_hit_stream_result(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertTrue(payload["no_public_speedup_claim"])
        self.assertEqual(
            payload["backends"],
            [
                raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND,
                raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND,
            ],
        )
        self.assertEqual(payload["row_counts"], [250000, 1000000])
        self.assertEqual(payload["modes"], ["count", "sum"])
        self.assertIn("NVIDIA RTX A5000", payload["nvidia_smi"])

        by_key = {
            (case["row_count"], case["mode"], case["backend"]): case
            for case in payload["cases"]
        }
        expected_min_hit_stream_slowdown = {
            (250000, "count"): 20.0,
            (250000, "sum"): 100.0,
            (1000000, "count"): 20.0,
            (1000000, "sum"): 100.0,
        }
        for key, min_slowdown in expected_min_hit_stream_slowdown.items():
            row_count, mode = key
            grouped = by_key[(row_count, mode, raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND)]
            hit_stream = by_key[
                (row_count, mode, raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND)
            ]
            slowdown = hit_stream["median_wall_sec"] / grouped["median_wall_sec"]
            with self.subTest(row_count=row_count, mode=mode):
                self.assertTrue(grouped["matches_cpu_reference"])
                self.assertTrue(hit_stream["matches_cpu_reference"])
                self.assertTrue(grouped["prepared_steady_state"])
                self.assertTrue(hit_stream["prepared_steady_state"])
                self.assertFalse(grouped["native_device_column_path_used"])
                self.assertTrue(hit_stream["native_device_column_path_used"])
                self.assertGreater(slowdown, min_slowdown)

    def test_report_records_primitive_first_design_correction(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RayDB Prepared Grouped-Reduction Opponent", text)
        self.assertIn("good negative result", text)
        self.assertIn("primitive-first rather than hit-stream-first", text)
        self.assertIn("27.5x slower", text)
        self.assertIn("140.5x slower", text)
        self.assertIn("true-zero-copy wording", text)
        self.assertIn("future v3.0 extension lane", text)


if __name__ == "__main__":
    unittest.main()
