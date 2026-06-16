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


class Goal4471V30M75TrianglePhaseSplitTest(unittest.TestCase):
    def test_phase_split_math_separates_build_once_from_replay(self) -> None:
        payload = app._segmented_phase_split_ms(
            segment_query_schedule="prepared_segment_replay",
            warmup=1,
            repeat=3,
            measured_query_timings_ms=[5.0, 7.0, 9.0],
            warmup_query_timings_ms=[11.0],
            build_once_ms={"prepare_scene": 10.0, "segment_ray_build": 30.0},
            per_run_build_timings_ms={},
            run_backend_ms=72.0,
        )

        self.assertEqual("triangle_counting.segmented_phase_split.v1", payload["schema_version"])
        self.assertEqual("prepared_segment_replay", payload["segment_query_schedule"])
        self.assertEqual(40.0, payload["build_once_total_ms"])
        self.assertEqual(21.0, payload["measured_replay_query_total_ms"])
        self.assertEqual(7.0, payload["measured_replay_query_median_ms"])
        self.assertAlmostEqual(3.0 * 1000.0 / 21.0, payload["replay_queries_per_second"])
        self.assertAlmostEqual(40.0 / 3.0, payload["amortized_build_per_measured_query_ms"])
        self.assertAlmostEqual(40.0 + 7.0, payload["one_shot_backend_estimate_ms"])
        self.assertIn("build-once", payload["legacy_timing_note"])

    def test_segmented_app_emits_phase_split_metadata_without_changing_legacy_timing(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn('"phase_split_ms": phase_split_ms', source)
        self.assertIn('"schema_version": "triangle_counting.segmented_phase_split.v1"', source)
        self.assertIn('"segment_ray_build_total_ms"', source)
        self.assertIn("legacy_timing_note", source)

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_segmented_scene_prepared_replay_reports_phase_split(self) -> None:
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
                "rt_graph_2a1_segmented_scene_generic_rt",
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                warmup=1,
                repeat=2,
                segment_max_two_hop_rows=100,
                scene_max_directed_edges=100,
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
            )

        phase = payload["phase_split_ms"]
        self.assertEqual("prepared_segment_replay", phase["segment_query_schedule"])
        self.assertGreater(phase["build_once_total_ms"], 0.0)
        self.assertGreater(phase["measured_replay_query_total_ms"], 0.0)
        self.assertEqual(2, phase["measured_replay_query_runs"])
        self.assertIn("triangle_build", phase["build_once_ms"])
        self.assertTrue(payload["prepared_session_residency"]["prepare_once_query_many_pattern"])
        self.assertEqual(payload["generic_rt_weighted_triangle_count"], 4)


if __name__ == "__main__":
    unittest.main()
