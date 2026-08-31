from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5158VectorizedNearestCellMbrSeedTest(unittest.TestCase):
    def test_seed_uses_cell_id_tie_break_before_exact_point_tie_break(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [20, 10],
            "x": [-1.0, 1.0],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        query_points = {
            "ids": [100],
            "x": [0.0],
            "y": [0.0],
            "z": [0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
        )

        seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor="numpy",
            return_metadata=True,
        )

        self.assertEqual(seed["metadata"]["cell_mbr_selection"], "numpy_vectorized_ordered_argmin_min_distance_then_cell_id")
        self.assertEqual(seed["metadata"]["seed_point_reduction_strategy"], "vectorized_expand_lexsort")
        self.assertEqual(seed["columns"]["seed_cell_ids"].tolist(), [0])
        self.assertEqual(seed["columns"]["nearest_item_ids"].tolist(), [20])
        self.assertEqual(seed["columns"]["nearest_distances"].tolist(), [1.0])

    def test_vectorized_seed_keeps_public_contract_and_app_neutrality(self) -> None:
        import rtdsl as rt

        self.assertIn("seed_nearest_witness_from_nearest_cell_mbr_numpy_columns", rt.__all__)
        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def seed_nearest_witness_from_nearest_cell_mbr_numpy_columns")
        end = source.index("def cell_mbr_nearest_frontier_numpy_columns")
        generic_window = source[start:end].lower()
        self.assertIn("generic_seed_nearest_witness_from_nearest_cell_mbr", generic_window)
        self.assertIn("numpy_vectorized_ordered_argmin_min_distance_then_cell_id", generic_window)
        self.assertIn("vectorized_expand_lexsort", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)

    def test_vectorized_seed_profile_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_vectorized_seed_profile_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5158 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        sample1024 = {case["case"]: case for case in payload["cases"]}["sample1024"]
        self.assertTrue(sample1024["matched"])
        self.assertEqual(sample1024["rtdl"]["validation_mode"], "author-only")
        self.assertIsNone(sample1024["rtdl"]["rtdl_matches_exact_reference"])
        for direction in ("directed_a_to_b", "directed_b_to_a"):
            timings = sample1024["rtdl"][direction]["phase_timings_sec_median"]
            self.assertLess(timings["initial_state_seed"], 0.025)
            self.assertGreater(timings["frontier_rows"], 0.0)


if __name__ == "__main__":
    unittest.main()
