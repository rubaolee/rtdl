from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan import (
    rtdl_rt_dbscan_benchmark_app as dbscan_app,
)
from tests._embree_support import embree_available


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"


def _load_rtnn_runner():
    spec = importlib.util.spec_from_file_location("goal2348_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load RTNN runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FakeRow:
    def __init__(self, query_id: int, neighbor_id: int, distance: float) -> None:
        self.query_id = query_id
        self.neighbor_id = neighbor_id
        self.distance = distance


class _FakeRows:
    def __init__(self, rows: tuple[_FakeRow, ...]) -> None:
        self.rows_ptr = rows

    def __len__(self) -> int:
        return len(self.rows_ptr)


class Goal2627EmbreeCoverageForOptixOnlyBenchmarksTest(unittest.TestCase):
    @unittest.skipUnless(embree_available(), "Embree runtime is not available")
    def test_rt_dbscan_embree_rows_match_tiny_reference(self) -> None:
        payload = dbscan_app.run_rt_dbscan_benchmark(
            mode="embree_prepared_rows",
            dataset="tiny",
            point_count=None,
            radius=None,
            min_neighbors=None,
            seed=20260526,
            partner="cupy",
            include_rows=False,
            validate=True,
        )

        self.assertEqual(payload["mode"], "embree_prepared_rows")
        self.assertTrue(payload["matches_reference"])
        self.assertEqual(payload["metadata"]["native_engine_row_contract"], "generic_fixed_radius_neighbors_3d_rows")
        self.assertFalse(payload["metadata"]["rt_core_accelerated"])

    def test_rtnn_embree_summary_adapter_matches_optix_row_schema(self) -> None:
        runner = _load_rtnn_runner()
        rows = _FakeRows(
            (
                _FakeRow(10, 3, 0.3),
                _FakeRow(10, 2, 0.1),
                _FakeRow(20, 7, 0.2),
            )
        )

        summaries = runner._ranked_summary_rows_from_fixed_radius_row_view(rows, (10, 20, 30))

        self.assertEqual(
            tuple(summaries[0]),
            (
                "query_id",
                "neighbor_count",
                "nearest_neighbor_id",
                "kth_neighbor_id",
                "nearest_distance",
                "kth_distance",
                "sum_distance",
            ),
        )
        self.assertEqual(summaries[0]["nearest_neighbor_id"], 2)
        self.assertEqual(summaries[0]["kth_neighbor_id"], 3)
        self.assertEqual(summaries[1]["neighbor_count"], 1)
        self.assertEqual(summaries[2]["nearest_neighbor_id"], 0xFFFFFFFF)


if __name__ == "__main__":
    unittest.main()
