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
RTDSL_INIT = ROOT / "src/rtdsl/__init__.py"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_CUDA_HELPERS = ROOT / "src/native/optix/rtdl_optix_cuda_helpers.cu"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4477V30M81TriangleCompactConstantRayBatchTest(unittest.TestCase):
    def test_compact_constant_ray_batch_symbol_is_generic_and_wired(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        init_source = RTDSL_INIT.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        helpers = OPTIX_CUDA_HELPERS.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")

        symbol = "rtdl_optix_ray_batch_3d_create_device_xz_constant_y_direction"
        self.assertIn(symbol, runtime)
        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn("rtdl_cuda_pack_ray3d_xz_constant_y_direction_precompiled", helpers)
        self.assertIn("prepare_ray_batch_device_xz_constant_y_direction", runtime)
        self.assertIn("pack_optix_ray_batch_3d_device_xz_constant_y_direction_inputs", runtime)
        self.assertIn("pack_optix_ray_batch_3d_device_xz_constant_y_direction_inputs", init_source)
        self.assertIn("compact_constant_ray_columns", runtime)
        self.assertIn("partner_device_xz_constant_y_direction", runtime)
        self.assertNotIn("triangle_counting", api + workloads + helpers + prelude)
        self.assertNotIn("rt_graph", api + workloads + helpers + prelude)

    def test_triangle_app_exposes_explicit_compact_layout_choice(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--segment-ray-column-layout", source)
        self.assertIn('choices=("full", "xz_constant_y_direction")', source)
        self.assertIn("_prepare_rt_graph_2a1_segment_ray_batch", source)
        self.assertIn("compact_constant_ray_batch", source)
        self.assertIn("segment_ray_column_layout", source)
        self.assertIn("origin_y=-0.1", source)
        self.assertIn("direction=(0.0, 1.0, 0.0)", source)
        self.assertIn("tmax=0.2", source)

    def test_compact_layout_requires_prepared_segment_replay(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires segment_query_schedule prepared_segment_replay"):
            app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file="missing.edge",
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                segment_ray_representation="unique_weighted",
                segment_query_schedule="per_run",
                segment_ray_column_layout="xz_constant_y_direction",
            )

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_compact_constant_layout_matches_k4_oracle(self) -> None:
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
                segment_ray_column_layout="xz_constant_y_direction",
                validate_oracle=True,
            )

        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(4, payload["generic_rt_weighted_triangle_count"])
        self.assertEqual("xz_constant_y_direction", payload["segmentation"]["segment_ray_column_layout"])
        self.assertTrue(payload["primitive_layout"]["compact_constant_ray_batch"])
        self.assertGreater(payload["timing_ms"]["prepared_ray_batch_build_median_ms"], 0.0)
        summary = payload["generic_rt_summary"]["last_segment_summary"]
        self.assertTrue(summary["prepared_ray_batch_used"])
        self.assertEqual(
            "PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_ANY_HIT_WEIGHTED_SUM_DEVICE_WEIGHTS_V1",
            summary["contract"],
        )
        metadata = summary["transfer_metadata"]
        self.assertEqual("partner_device_xz_constant_y_direction", metadata["ray_batch_created_from"])
        self.assertTrue(metadata["compact_constant_ray_columns"])
        self.assertFalse(metadata["query_rays_uploaded_each_run"])
        self.assertTrue(metadata["prepared_rays_resident_on_device"])


if __name__ == "__main__":
    unittest.main()
