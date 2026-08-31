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
    / "build_xhd_goal5358_author_like_radius_queue_reference.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5358_author_like_radius_queue_reference.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5358_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5358AuthorLikeRadiusQueueReferenceTest(unittest.TestCase):
    def test_author_like_reference_matches_bounded3d_author_iteration_fields(self):
        payload = _load_module().build_artifact()
        self.assertEqual(
            "author_like_radius_queue_reference_matches_bounded3d_author_trace",
            payload["status"],
        )
        self.assertTrue(payload["comparison"]["matched"])
        self.assertEqual(0, payload["comparison"]["mismatch_count"])
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
        self.assertEqual(author_core, payload["rtdl_reference"]["iterations"])
        self.assertEqual(2.0, payload["rtdl_reference"]["hd_result"])

    def test_reference_uses_generic_nearest_pipeline_but_does_not_enable_tune_radius(self):
        payload = _load_module().build_artifact()
        metadata = payload["rtdl_reference"]["pipeline_metadata"]
        self.assertEqual("none", metadata["app_semantics"])
        self.assertIn("generic_pairwise_l2_distance_candidate_rows", metadata["contract"])
        self.assertIn("generic_nearest_witness_columns", metadata["contract"])
        self.assertIn("generic_max_nearest_distance_with_witness", metadata["contract"])
        self.assertTrue(payload["rtdl_reference"]["uses_generic_nearest_pipeline"])
        self.assertFalse(payload["decision"]["current_cell_mbr_route_replaced"])
        self.assertFalse(payload["decision"]["explicit_author_tune_radius_supported"])

    def test_saved_artifact_preserves_claim_boundary(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["comparison"]["matched"])
        self.assertIn("route_implementation_still_required", payload["exit_label"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
