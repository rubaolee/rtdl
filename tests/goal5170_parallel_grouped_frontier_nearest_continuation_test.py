from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _numba_available() -> bool:
    try:
        import numba  # noqa: F401
    except Exception:
        return False
    return True


class Goal5170ParallelGroupedFrontierNearestContinuationTest(unittest.TestCase):
    def _fixture(self):
        import rtdsl as rt

        query_points = {
            "ids": [100, 101],
            "x": [0.0, 10.0],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        target_points = {
            "ids": [50, 20, 10, 5, 30, 40],
            "x": [5.0, 1.0, 9.0, 1.0, 11.0, 9.0],
            "y": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        }
        cell_columns = {
            "point_row_indices": [0, 1, 2, 3, 4, 5],
        }
        row_table = {
            "columns": {
                "frontier_kind_codes": [
                    rt.CELL_MBR_FRONTIER_KIND_CODES["inline"],
                    rt.CELL_MBR_FRONTIER_KIND_CODES["offload"],
                    rt.CELL_MBR_FRONTIER_KIND_CODES["inline"],
                    rt.CELL_MBR_FRONTIER_KIND_CODES["pruned"],
                    rt.CELL_MBR_FRONTIER_KIND_CODES["offload"],
                ],
                "query_row_ids": [0, 1, 0, 0, 1],
                "point_begin_offsets": [0, 2, 3, 4, 4],
                "point_counts": [2, 1, 1, 1, 2],
            }
        }
        return rt, query_points, target_points, cell_columns, row_table

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_parallel_grouped_frontier_matches_numpy_and_serial_numba(self) -> None:
        rt, query_points, target_points, cell_columns, row_table = self._fixture()

        kwargs = {
            "coordinate_fields": ("x", "y", "z"),
            "current_best_distances": [float("inf"), 1.0],
            "current_best_item_ids": [-1, 8],
            "return_metadata": True,
        }
        numpy_nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            cell_columns,
            row_table,
            executor="numpy",
            **kwargs,
        )
        serial_nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            cell_columns,
            row_table,
            executor="numba",
            **kwargs,
        )
        parallel_nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            cell_columns,
            row_table,
            executor="numba_parallel",
            **kwargs,
        )

        self.assertEqual(parallel_nearest["metadata"]["executor"], "numba_parallel")
        self.assertEqual(
            parallel_nearest["metadata"]["reduction_strategy"],
            "numba_parallel_grouped_query_loop_min_distance_then_item_id",
        )
        self.assertEqual(parallel_nearest["metadata"]["used_frontier_row_count"], 4)
        self.assertEqual(parallel_nearest["metadata"]["candidate_distance_evaluations"], 6)
        for key in ("nearest_item_ids", "nearest_distances"):
            self.assertEqual(
                parallel_nearest["columns"][key].tolist(),
                numpy_nearest["columns"][key].tolist(),
                key,
            )
            self.assertEqual(
                parallel_nearest["columns"][key].tolist(),
                serial_nearest["columns"][key].tolist(),
                key,
            )
        self.assertEqual(parallel_nearest["columns"]["nearest_item_ids"].tolist(), [5, 8])
        self.assertEqual(parallel_nearest["columns"]["nearest_distances"].tolist(), [1.0, 1.0])

    def test_auto_executor_exposes_parallel_when_numba_is_available(self) -> None:
        rt, query_points, target_points, cell_columns, row_table = self._fixture()

        nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            cell_columns,
            row_table,
            coordinate_fields=("x", "y", "z"),
            current_best_distances=[float("inf"), 1.0],
            current_best_item_ids=[-1, 8],
            executor="auto",
            return_metadata=True,
        )

        self.assertIn(nearest["metadata"]["executor"], ("numpy", "numba_parallel"))
        self.assertEqual(nearest["metadata"]["contract"], "generic_nearest_witness_from_cell_mbr_frontier")
        self.assertEqual(nearest["metadata"]["app_semantics"], "none")

    def test_parallel_frontier_source_window_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def _nearest_witness_from_frontier_parallel_by_query_loop_impl")
        end = source.index("def _validate_group_count")
        generic_window = source[start:end].lower()

        self.assertIn("prange", generic_window)
        self.assertIn("query", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)

    def test_parallel_frontier_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_res4full_goal5170_parallel_frontier_continuation_matrix_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5170 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        case = {case["case"]: case for case in payload["cases"]}["res4full"]
        self.assertTrue(case["matched"])
        self.assertEqual(case["rtdl"]["validation_mode"], "author-only")
        self.assertIsNone(case["ratio_policy"]["author_avg_vs_rtdl_route_ratio"])
        for direction in ("directed_a_to_b", "directed_b_to_a"):
            self.assertEqual(
                case["rtdl"][direction]["nearest_reduction_strategy"],
                "numba_parallel_grouped_query_loop_min_distance_then_item_id",
            )


if __name__ == "__main__":
    unittest.main()
