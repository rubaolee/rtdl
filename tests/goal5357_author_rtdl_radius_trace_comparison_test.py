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
    / "build_xhd_goal5357_author_rtdl_radius_trace_comparison.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5357_author_rtdl_radius_trace_comparison.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5357_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5357AuthorRtdlRadiusTraceComparisonTest(unittest.TestCase):
    def test_build_artifact_separates_value_match_from_trace_mismatch(self):
        payload = _load_module().build_artifact()
        self.assertEqual(
            "trace_comparison_complete__rtdl_value_matches_but_radius_trace_not_author_queue_aligned",
            payload["status"],
        )
        summary = payload["summary"]
        self.assertTrue(summary["hd_result_matched"])
        self.assertFalse(summary["trace_matched"])
        self.assertFalse(summary["trace_comparable_as_author_radius_queue"])
        self.assertTrue(summary["explicit_author_tune_radius_must_remain_fail_closed"])
        self.assertGreaterEqual(summary["semantic_mismatch_count"], 4)

    def test_bounded3d_comparison_records_specific_author_vs_rtdl_semantic_mismatches(self):
        comparison = _load_module().build_artifact()["comparison"]
        self.assertEqual("bounded3d_author_vs_rtdl_single_pass", comparison["case_id"])
        self.assertEqual(2.0, comparison["author"]["hd_result"])
        self.assertEqual(2.0, comparison["rtdl"]["hd_result"])
        self.assertTrue(comparison["value_result"]["hd_result_matched"])

        self.assertEqual("author_adaptive_radius_queue_loop", comparison["author"]["iteration_model"])
        self.assertEqual(
            "single_pass_cell_mbr_route_not_author_radius_loop",
            comparison["rtdl"]["iteration_model"],
        )
        self.assertEqual(2.0, comparison["author"]["first_iteration"]["radius"])
        self.assertAlmostEqual(3.3166247913554, comparison["rtdl"]["first_direction"]["radius"])
        self.assertEqual(0, comparison["author"]["first_iteration"]["num_output_points"])
        self.assertEqual(9, comparison["rtdl"]["first_direction"]["num_output_points"])

        mismatch_fields = {
            row["field"] for row in comparison["trace_result"]["semantic_mismatches"]
        }
        self.assertIn("iteration_model", mismatch_fields)
        self.assertIn("radius", mismatch_fields)
        self.assertIn("num_output_points", mismatch_fields)
        self.assertIn("route_uses_radius_growth_helper", mismatch_fields)

    def test_saved_artifact_preserves_claim_boundary_and_forbidden_tune_radius_claim(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(payload["summary"]["trace_matched"])
        self.assertTrue(payload["summary"]["explicit_author_tune_radius_must_remain_fail_closed"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)
        self.assertIn("keep_explicit_tune_radius_fail_closed", payload["exit_label"])


if __name__ == "__main__":
    unittest.main()
