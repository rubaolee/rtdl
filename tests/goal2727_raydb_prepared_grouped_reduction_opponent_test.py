import inspect
import unittest

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb
from scripts import goal2685_raydb_device_hit_stream_handoff_pod_runner as runner


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


if __name__ == "__main__":
    unittest.main()
