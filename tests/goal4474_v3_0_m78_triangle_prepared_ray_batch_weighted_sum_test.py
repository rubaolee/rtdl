from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from examples.current.research_benchmarks.triangle_counting import rt_graph_contract as contract_mod
from examples.current.research_benchmarks.triangle_counting import rtdl_triangle_counting_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4474V30M78TrianglePreparedRayBatchWeightedSumTest(unittest.TestCase):
    def test_generic_prepared_ray_batch_weighted_sum_symbol_is_wired(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")

        symbol = "rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights"
        self.assertIn(symbol, runtime)
        self.assertIn(symbol, api)
        self.assertIn("run_prepared_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum", workloads)
        self.assertIn(symbol, prelude)
        self.assertIn("ray_batch_any_hit_weighted_sum_device_weights", runtime)
        self.assertIn("_device_ray_expected_device", runtime)

    def test_triangle_prepared_replay_uses_prepared_ray_batch(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("prepare_ray_batch_device_columns", source)
        self.assertIn("ray_batch_any_hit_weighted_sum_device_weights", source)
        self.assertIn("prepared_ray_batch_build", source)

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_segmented_prepared_replay_reports_prepared_ray_batch_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            edge_file = Path(tmp) / "k4.edge"
            contract_mod.write_binary_edges(
                edge_file,
                (
                    (0, 1),
                    (0, 2),
                    (0, 3),
                    (1, 2),
                    (1, 3),
                    (2, 3),
                ),
            )
            payload = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                warmup=1,
                repeat=2,
                segment_max_two_hop_rows=100,
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="cupy_repeat",
                validate_oracle=True,
            )

        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(4, payload["generic_rt_weighted_triangle_count"])
        self.assertGreater(payload["timing_ms"]["prepared_ray_batch_build_median_ms"], 0.0)
        self.assertIn("prepared_ray_batch_build", payload["phase_split_ms"]["build_once_ms"])
        summary = payload["generic_rt_summary"]["last_segment_summary"]
        self.assertTrue(summary["prepared_ray_batch_used"])
        self.assertEqual(
            "PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_ANY_HIT_WEIGHTED_SUM_DEVICE_WEIGHTS_V1",
            summary["contract"],
        )
        self.assertTrue(summary["transfer_metadata"]["prepared_rays_resident_on_device"])
        self.assertFalse(summary["transfer_metadata"]["query_rays_uploaded_each_run"])


if __name__ == "__main__":
    unittest.main()
