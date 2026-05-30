import unittest
from pathlib import Path

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "raydb_style" / "rtdl_raydb_style_benchmark_app.py"
RUNNER = ROOT / "scripts" / "goal2685_raydb_device_hit_stream_handoff_pod_runner.py"


class Goal2720RaydbPreparedDeviceHitStreamSteadyStateTest(unittest.TestCase):
    def test_prepared_backend_is_registered_but_keeps_boundary(self) -> None:
        self.assertEqual(
            raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND,
            "paper_rt_optix_device_hit_stream_triton_prepared",
        )
        self.assertIn(raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND, raydb.BACKENDS)

        source = APP.read_text(encoding="utf-8")
        self.assertIn("def _run_paper_rt_prepared_device_hit_stream_triton_result_mode", source)
        self.assertIn("prepare_paper_rt_encoded_table_descriptor", source)
        self.assertIn("rt.prepare_optix_static_triangle_scene_3d", source)
        self.assertIn("prepared_scene.ray_triangle_hit_stream_device_columns", source)
        self.assertIn("prepared_payload_columns_reused", source)
        self.assertIn("prepared_optix_scene_reused", source)
        self.assertIn('group_id_bounds_validation="caller_asserted"', source)
        self.assertIn("Native execution still owns only generic RT traversal", source)
        self.assertNotIn("raydb", "rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns")

    def test_pod_runner_uses_internal_repeat_for_prepared_backend(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")

        self.assertIn("PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND", source)
        self.assertIn("prepared_iteration_wall_sec", source)
        self.assertIn("prepared_payload_columns_reused", source)
        self.assertIn("prepared_optix_scene_reused", source)
        self.assertIn("starting prepared backend", source)


if __name__ == "__main__":
    unittest.main()
