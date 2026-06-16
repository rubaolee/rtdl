from __future__ import annotations

from pathlib import Path
import unittest

from examples.current.research_benchmarks.triangle_counting import rtdl_triangle_counting_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"


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


if __name__ == "__main__":
    unittest.main()
