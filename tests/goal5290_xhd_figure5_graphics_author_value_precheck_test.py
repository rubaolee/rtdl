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
    / "build_xhd_figure5_graphics_author_value_precheck.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5290_figure5_graphics_author_value_precheck_2026-07-09.json"
)
RAW_POD_PROBE = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5290_author_value_probe_raw_pod_2026-07-09.json"
)
LOG_INDEX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_paper_branch_log_index_goal5176_2026-07-08.json"
)


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_figure5_graphics_author_value_precheck",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT.parent))
    spec.loader.exec_module(module)
    return module


class Goal5290XhdFigure5GraphicsAuthorValuePrecheckTest(unittest.TestCase):
    def test_builder_reconstructs_no_matching_candidate_decision(self):
        module = _load_script()
        artifact = module.build_precheck(
            log_index_path=LOG_INDEX,
            raw_probe_path=RAW_POD_PROBE,
            date="2026-07-09",
        )

        self.assertTrue(artifact["matched"])
        self.assertEqual(
            artifact["status"],
            "figure5_graphics_author_value_precheck_ready__no_available_candidate_matches_paper_log",
        )
        self.assertFalse(artifact["decision"]["continue_to_rtdl_timing"])
        self.assertEqual(artifact["decision"]["matching_candidate_labels"], [])

    def test_artifact_compares_available_author_variants_to_paper_log_value(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        target = payload["paper_log_target"]
        candidates = {row["label"]: row for row in payload["candidate_author_runs"]}

        self.assertEqual(target["pair"], ["dragon.ply", "asian_dragon.ply"])
        self.assertAlmostEqual(target["paper_log_hd_result"], 0.06536811590194702)
        self.assertEqual(target["record_count"], 5)
        self.assertEqual(sorted(candidates), ["scaled_1e-3", "unscaled"])
        self.assertAlmostEqual(candidates["unscaled"]["stdout_hd_result"], 52.4535)
        self.assertAlmostEqual(candidates["scaled_1e-3"]["stdout_hd_result"], 0.0654553)
        self.assertFalse(candidates["unscaled"]["matches_paper_log_value"])
        self.assertFalse(candidates["scaled_1e-3"]["matches_paper_log_value"])
        self.assertGreater(candidates["scaled_1e-3"]["abs_diff_vs_paper_log"], 1e-5)

    def test_claim_boundary_forbids_figure5_ratio_and_rtdl_timing(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for value in payload["claim_boundary"].values():
            self.assertFalse(value)
        self.assertFalse(payload["decision"]["continue_to_rtdl_timing"])
        self.assertIn(
            "move to another figure/blocker rather than timing a value-mismatched candidate",
            payload["decision"]["next_options"],
        )


if __name__ == "__main__":
    unittest.main()
