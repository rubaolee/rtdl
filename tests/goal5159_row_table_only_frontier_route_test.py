from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5159RowTableOnlyFrontierRouteTest(unittest.TestCase):
    def test_route_requests_row_table_only_from_native_frontier_helper(self) -> None:
        script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_cell_mbr_frontier_route_gate.py"
        ).read_text(encoding="utf-8")
        native_call = script.index("rt.cell_mbr_nearest_frontier_native_3d_optix_columns")
        native_block_end = script.index("elif backend == \"numpy\"", native_call)
        native_block = script[native_call:native_block_end]
        self.assertIn("return_split_frontiers=False", native_block)
        self.assertIn("emit_pruned_rows=False", native_block)

    def test_helper_default_keeps_split_frontiers_for_backward_compatibility(self) -> None:
        import rtdsl as rt

        query_points = {
            "ids": [100],
            "x": [0.0],
            "y": [0.0],
            "z": [0.0],
        }
        target_points = {
            "ids": [200, 201],
            "x": [0.0, 2.0],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
        )
        frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=10.0,
            current_best_distances=[float("inf")],
            current_best_item_ids=[-1],
            max_inline_points=2,
            return_metadata=True,
        )
        self.assertIn("row_table", frontier)
        self.assertIn("inline_frontier", frontier)
        self.assertIn("offload_frontier", frontier)
        self.assertIn("pruned_frontier", frontier)

    def test_row_table_only_artifact_preserves_claim_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_row_table_only_frontier_profile_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5159 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        self.assertFalse(payload["author_performance_parity_claimed"])
        sample1024 = {case["case"]: case for case in payload["cases"]}["sample1024"]
        self.assertTrue(sample1024["matched"])
        self.assertEqual(sample1024["rtdl"]["validation_mode"], "author-only")
        self.assertLess(sample1024["rtdl"]["route_sec_median"], 0.12)
        self.assertGreater(sample1024["rtdl"]["directed_a_to_b"]["frontier_row_count"], 100000)


if __name__ == "__main__":
    unittest.main()
