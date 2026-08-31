from __future__ import annotations

import importlib
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "librts_spatial_index"
    / "rtdl_librts_spatial_index_benchmark_app.py"
)
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4339_librts_skip_counts_for_native_aabb_perf_2026-06-11.md"
)
APP = importlib.import_module(
    "examples.current.research_benchmarks.librts_spatial_index.rtdl_librts_spatial_index_benchmark_app"
)


class _FakePreparedEmbree:
    scene_prepare_sec = 0.001

    def count(self, **_: object) -> dict[str, object]:
        return {
            "primitive": "AABB_INDEX_QUERY_2D",
            "contract": "generic_prepared_aabb_index_query_2d",
            "counts": {"point_contains": 7, "range_contains": 3, "range_intersects": 11},
            "candidate_checks": 123,
            "index": {"indexed_boxes": 2},
            "run_phases": {"query_aabb_index_2d_sec": 0.002},
        }

    def close(self) -> None:
        return None


class Goal4339LibrtsSkipCountsNativePerfGuardTest(unittest.TestCase):
    def test_embree_skip_counts_avoids_quadratic_cpu_oracle(self) -> None:
        fixture = APP.make_uniform_fixture(box_count=2, query_count=2, seed=4339)
        with mock.patch.object(APP.rt, "prepare_aabb_index_2d", return_value=_FakePreparedEmbree()):
            with mock.patch.object(APP, "run_counts", side_effect=AssertionError("oracle should be skipped")):
                payload = APP.run_embree_aabb_counts(
                    fixture,
                    "all",
                    query_repeat=2,
                    warmup=1,
                    validate_reference=False,
                )

        self.assertEqual(payload["counts"], {"point_contains": 7, "range_contains": 3, "range_intersects": 11})
        self.assertIsNone(payload["matches_cpu_reference"])
        self.assertTrue(payload["cpu_reference_skipped"])
        self.assertEqual(payload["repeat_protocol"]["measured_run_count"], 2)
        self.assertEqual(payload["run_phases"]["query_repeat"], 2)

    def test_embree_default_still_validates_against_cpu_oracle(self) -> None:
        fixture = APP.make_uniform_fixture(box_count=2, query_count=2, seed=4340)
        expected_counts = {"point_contains": 7, "range_contains": 3, "range_intersects": 11}
        with mock.patch.object(APP.rt, "prepare_aabb_index_2d", return_value=_FakePreparedEmbree()):
            with mock.patch.object(APP, "run_counts", return_value={"counts": expected_counts}) as run_counts:
                payload = APP.run_embree_aabb_counts(
                    fixture,
                    "all",
                    query_repeat=1,
                    warmup=0,
                )

        run_counts.assert_called_once()
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertFalse(payload["cpu_reference_skipped"])

    def test_cli_skip_counts_is_passed_to_native_aabb_modes(self) -> None:
        text = APP_PATH.read_text(encoding="utf-8")
        self.assertIn("validate_reference=not args.skip_counts", text)
        self.assertGreaterEqual(text.count("validate_reference=not args.skip_counts"), 2)
        self.assertIn('"cpu_reference_skipped": not validate_reference', text)
        self.assertIn('"matches_cpu_reference": matches_cpu_reference', text)

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal4339", text)
        self.assertIn("O(boxes x queries) Python CPU oracle", text)
        self.assertIn("--skip-counts", text)
        self.assertIn("matches_cpu_reference: null", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
