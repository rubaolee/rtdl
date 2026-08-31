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


class Goal5168ParallelNearestCellMbrSeedTest(unittest.TestCase):
    def _fixture(self):
        import rtdsl as rt

        target_points = {
            "ids": [30, 20, 10, 40, 50, 60],
            "x": [-1.0, 1.0, 1.1, 5.0, 5.2, 8.0],
            "y": [0.0, 0.0, 0.1, 0.0, 0.3, 0.0],
            "z": [0.0, 0.2, 0.0, 0.0, 0.1, 0.0],
        }
        query_points = {
            "ids": [100, 101, 102, 103],
            "x": [0.0, 1.05, 4.9, 7.7],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(4, 2, 1),
        )
        return rt, query_points, target_points, grid

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_parallel_seed_matches_numpy_and_serial_numba(self) -> None:
        rt, query_points, target_points, grid = self._fixture()

        numpy_seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor="numpy",
            return_metadata=True,
        )
        serial_seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor="numba",
            return_metadata=True,
        )
        parallel_seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor="numba_parallel",
            return_metadata=True,
        )

        self.assertEqual(parallel_seed["metadata"]["executor"], "numba_parallel")
        self.assertEqual(
            parallel_seed["metadata"]["cell_mbr_selection"],
            "numba_parallel_loop_min_distance_then_cell_id",
        )
        for key in ("nearest_item_ids", "nearest_distances", "seed_cell_ids"):
            self.assertEqual(
                parallel_seed["columns"][key].tolist(),
                numpy_seed["columns"][key].tolist(),
                key,
            )
            self.assertEqual(
                parallel_seed["columns"][key].tolist(),
                serial_seed["columns"][key].tolist(),
                key,
            )

    def test_auto_executor_exposes_parallel_when_numba_is_available(self) -> None:
        rt, query_points, target_points, grid = self._fixture()

        seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor="auto",
            return_metadata=True,
        )

        allowed = ("numpy", "numba_parallel")
        self.assertIn(seed["metadata"]["executor"], allowed)
        self.assertEqual(seed["metadata"]["contract"], "generic_seed_nearest_witness_from_nearest_cell_mbr")
        self.assertEqual(seed["metadata"]["app_semantics"], "none")

    def test_parallel_seed_source_window_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def _seed_nearest_witness_parallel_loop_impl")
        end = source.index("def _nearest_witness_from_frontier_loop_impl")
        generic_window = source[start:end].lower()

        self.assertIn("prange", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)

    def test_parallel_seed_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_res4full_goal5168_parallel_seed_matrix_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5168 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        case = {case["case"]: case for case in payload["cases"]}["res4full"]
        self.assertTrue(case["matched"])
        self.assertEqual(case["rtdl"]["validation_mode"], "author-only")
        self.assertIsNone(case["ratio_policy"]["author_avg_vs_rtdl_route_ratio"])
        self.assertGreater(case["rtdl"]["route_sec_median"], 0.0)
        for direction in ("directed_a_to_b", "directed_b_to_a"):
            self.assertEqual(
                case["rtdl"][direction]["initial_cell_mbr_selection"],
                "numba_parallel_loop_min_distance_then_cell_id",
            )


if __name__ == "__main__":
    unittest.main()
