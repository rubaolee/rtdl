from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from examples.current.research_benchmarks.triangle_counting import rt_graph_contract as contract_mod
from examples.current.research_benchmarks.triangle_counting import rtdl_triangle_counting_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4481V30M85TriangleFusedDecodeProjectCandidateTest(unittest.TestCase):
    def test_fused_decode_project_output_builder_is_explicit_cli_choice(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--segment-ray-output-builder", source)
        self.assertIn('choices=("cupy_vectorized", "numba_fused_decode_project")', source)
        self.assertIn("_get_rt_graph_2a1_fill_weighted_rays_numba_kernel", source)
        self.assertIn("numba_fused_decode_project", source)

    def test_fused_decode_project_rejects_unsupported_layout(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires unique_weighted rays and full ray columns"):
            app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file="missing.edge",
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="numba_direct_sort_rle",
                segment_ray_column_layout="xz_constant_y_direction",
                segment_ray_output_builder="numba_fused_decode_project",
            )

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_fused_decode_project_matches_cupy_vectorized_on_k4(self) -> None:
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
            common = {
                "edge_file": str(edge_file),
                "edge_format": "binary",
                "backend": "optix",
                "detail": "summary",
                "partner": "cupy",
                "warmup": 1,
                "repeat": 1,
                "segment_max_two_hop_rows": 100,
                "segment_ray_representation": "unique_weighted",
                "segment_query_schedule": "prepared_segment_replay",
                "segment_unique_key_builder": "numba_direct_sort_rle",
                "segment_ray_build_telemetry": "sync_subphases",
                "validate_oracle": True,
            }
            cupy_vectorized = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                **common,
                segment_ray_output_builder="cupy_vectorized",
            )
            fused = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                **common,
                segment_ray_output_builder="numba_fused_decode_project",
            )

        self.assertTrue(cupy_vectorized["triangle_count_matches_oracle"])
        self.assertTrue(fused["triangle_count_matches_oracle"])
        self.assertEqual(
            cupy_vectorized["generic_rt_weighted_triangle_count"],
            fused["generic_rt_weighted_triangle_count"],
        )
        self.assertEqual(cupy_vectorized["ray_count"], fused["ray_count"])
        self.assertEqual(
            cupy_vectorized["segmentation"]["lowered_ray_weight_sum"],
            fused["segmentation"]["lowered_ray_weight_sum"],
        )
        phase_names = set(fused["timing_ms"]["segment_ray_build_phase_summary_ms"]["phase_names"])
        self.assertIn("numba_fused_decode_project", phase_names)
        self.assertNotIn("ray_column_projection_full", phase_names)


if __name__ == "__main__":
    unittest.main()
