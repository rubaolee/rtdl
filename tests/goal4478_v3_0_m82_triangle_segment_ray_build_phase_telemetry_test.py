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


class Goal4478V30M82TriangleSegmentRayBuildPhaseTelemetryTest(unittest.TestCase):
    def test_segment_ray_build_subphase_telemetry_is_explicit_cli_choice(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--segment-ray-build-telemetry", source)
        self.assertIn('choices=("none", "sync_subphases")', source)
        self.assertIn("segment_ray_build_phase_summary_ms", source)
        self.assertIn("triangle_counting.segment_ray_build_phase_summary.v1", source)
        self.assertIn("numba_key_fill", source)
        self.assertIn("cupy_unique_counts", source)
        self.assertIn("ray_column_projection_full", source)
        self.assertIn("sync_subphases", source)

    def test_invalid_segment_ray_build_telemetry_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "none or sync_subphases"):
            app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file="missing.edge",
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="numba_direct",
                segment_ray_build_telemetry="timeline_magic",
            )

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_segment_ray_build_subphase_summary_is_reported(self) -> None:
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
                repeat=1,
                segment_max_two_hop_rows=100,
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="numba_direct",
                segment_ray_build_telemetry="sync_subphases",
                validate_oracle=True,
            )

        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(4, payload["generic_rt_weighted_triangle_count"])
        self.assertEqual("sync_subphases", payload["timing_ms"]["segment_ray_build_telemetry"])
        summary = payload["timing_ms"]["segment_ray_build_phase_summary_ms"]
        self.assertEqual("triangle_counting.segment_ray_build_phase_summary.v1", summary["schema_version"])
        self.assertEqual(1, summary["run_count"])
        phase_names = set(summary["phase_names"])
        self.assertIn("numba_key_fill", phase_names)
        self.assertIn("cupy_unique_counts", phase_names)
        self.assertIn("unique_decode_weights", phase_names)
        self.assertIn("ray_column_projection_full", phase_names)
        self.assertGreater(summary["phases"]["cupy_unique_counts"]["median_ms"], 0.0)


if __name__ == "__main__":
    unittest.main()
