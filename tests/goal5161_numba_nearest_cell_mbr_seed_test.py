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


class Goal5161NumbaNearestCellMbrSeedTest(unittest.TestCase):
    def _fixture(self):
        import rtdsl as rt

        target_points = {
            "ids": [30, 20, 10, 40],
            "x": [-1.0, 1.0, 1.1, 5.0],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100, 101],
            "x": [0.0, 4.9],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(3, 1, 1),
        )
        return rt, query_points, target_points, grid

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_numba_seed_matches_numpy_seed_and_preserves_tie_breaks(self) -> None:
        rt, query_points, target_points, grid = self._fixture()

        numpy_seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor="numpy",
            return_metadata=True,
        )
        numba_seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor="numba",
            return_metadata=True,
        )

        self.assertEqual(numba_seed["metadata"]["executor"], "numba")
        self.assertEqual(numba_seed["metadata"]["cell_mbr_selection"], "numba_loop_min_distance_then_cell_id")
        self.assertEqual(numba_seed["metadata"]["seed_point_reduction_strategy"], "numba_loop_min_distance_then_item_id")
        self.assertEqual(
            numba_seed["columns"]["seed_cell_ids"].tolist(),
            numpy_seed["columns"]["seed_cell_ids"].tolist(),
        )
        self.assertEqual(
            numba_seed["columns"]["nearest_item_ids"].tolist(),
            numpy_seed["columns"]["nearest_item_ids"].tolist(),
        )
        self.assertEqual(
            numba_seed["columns"]["nearest_distances"].tolist(),
            numpy_seed["columns"]["nearest_distances"].tolist(),
        )
        self.assertEqual(numba_seed["columns"]["seed_cell_ids"].tolist()[0], 0)
        self.assertEqual(numba_seed["columns"]["nearest_item_ids"].tolist()[0], 30)

    def test_auto_executor_keeps_public_contract(self) -> None:
        rt, query_points, target_points, grid = self._fixture()

        seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor="auto",
            return_metadata=True,
        )

        self.assertEqual(seed["metadata"]["contract"], "generic_seed_nearest_witness_from_nearest_cell_mbr")
        self.assertEqual(seed["metadata"]["app_semantics"], "none")
        self.assertIn(seed["metadata"]["executor"], ("numpy", "numba", "numba_parallel"))
        self.assertFalse(seed["metadata"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(seed["metadata"]["whole_app_speedup_claim_authorized"])

    def test_invalid_executor_fails_closed(self) -> None:
        rt, query_points, target_points, grid = self._fixture()

        with self.assertRaises(ValueError):
            rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                executor="xhd",
            )

    def test_seed_helper_source_window_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def seed_nearest_witness_from_nearest_cell_mbr_numpy_columns")
        end = source.index("def cell_mbr_nearest_frontier_numpy_columns")
        generic_window = source[start:end].lower()
        self.assertIn("executor", generic_window)
        self.assertIn("numba_loop_min_distance_then_cell_id", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)

    def test_numba_seed_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_numba_seed_profile_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5161 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        sample1024 = {case["case"]: case for case in payload["cases"]}["sample1024"]
        self.assertTrue(sample1024["matched"])
        self.assertEqual(sample1024["rtdl"]["validation_mode"], "author-only")
        self.assertIsNone(sample1024["rtdl"]["rtdl_matches_exact_reference"])
        for direction in ("directed_a_to_b", "directed_b_to_a"):
            self.assertEqual(sample1024["rtdl"][direction]["initial_cell_mbr_selection"], "numba_loop_min_distance_then_cell_id")
            self.assertLess(sample1024["rtdl"][direction]["phase_timings_sec_median"]["initial_state_seed"], 0.02)


if __name__ == "__main__":
    unittest.main()
