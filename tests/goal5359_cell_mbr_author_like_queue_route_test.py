import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5359_cell_mbr_author_like_queue_route.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5359_cell_mbr_author_like_queue_route.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5359_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5359CellMbrAuthorLikeQueueRouteTest(unittest.TestCase):
    def test_cell_mbr_queue_route_matches_bounded3d_author_trace(self):
        payload = _load_module().build_artifact()
        self.assertEqual(
            "cell_mbr_author_like_queue_route_matches_bounded3d_author_trace",
            payload["status"],
        )
        self.assertTrue(payload["comparison"]["matched"])
        self.assertEqual(0, payload["comparison"]["mismatch_count"])
        self.assertEqual("cell_mbr_author_like_radius_queue_route", payload["rtdl_route"]["route_iteration_model"])

        author_core = [
            {
                "Iteration": row["Iteration"],
                "Radius": row["Radius"],
                "NumInputPoints": row["NumInputPoints"],
                "NumOutputPoints": row["NumOutputPoints"],
                "CMax2": row["CMax2"],
            }
            for row in payload["author"]["iterations"]
        ]
        self.assertEqual(author_core, payload["rtdl_route"]["queue_rows"])

    def test_route_uses_cell_mbr_nearest_columns_not_only_reference_pipeline(self):
        payload = _load_module().build_artifact()
        route = payload["rtdl_route"]
        self.assertTrue(route["uses_cell_mbr_route"])
        self.assertTrue(route["uses_emitted_nearest_columns"])
        self.assertEqual("numpy", route["backend"])
        self.assertEqual(1, len(route["route_iterations"]))
        iteration = route["route_iterations"][0]
        self.assertEqual("generic_cell_mbr_nearest_frontier_reference", iteration["route_contract"])
        self.assertEqual("generic_nearest_witness_from_cell_mbr_frontier", iteration["nearest_columns_contract"])
        self.assertEqual("none", iteration["nearest_columns_app_semantics"])

    def test_saved_artifact_keeps_hd_exec_tune_radius_fail_closed_boundary(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["comparison"]["matched"])
        self.assertTrue(payload["decision"]["cell_mbr_author_like_queue_route_available_for_bounded3d"])
        self.assertFalse(payload["decision"]["explicit_author_tune_radius_supported_by_hd_exec"])
        self.assertIn("wrapper_integration_still_required", payload["exit_label"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
