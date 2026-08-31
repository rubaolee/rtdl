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
    / "build_xhd_figure5_dragon_happy_candidate_matrix.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json"
)
LOG_INDEX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_paper_branch_log_index_goal5176_2026-07-08.json"
)
AUTHOR_GATE = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json"
)
PHASE_MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_full_public_phase_matrix_goal5188_graphics_dragon_happy_buddha_2026-07-08.json"
)
RTDL_FRESH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json"
)
RTDL_WARM = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_full_public_all_source_goal5212_all_source_no_copy_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json"
)


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_figure5_dragon_happy_candidate_matrix",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT.parent))
    spec.loader.exec_module(module)
    return module


class Goal5291XhdFigure5DragonHappyCandidateMatrixTest(unittest.TestCase):
    def test_builder_reconstructs_value_matched_candidate(self):
        module = _load_script()
        artifact = module.build_matrix(
            log_index_path=LOG_INDEX,
            author_gate_path=AUTHOR_GATE,
            phase_matrix_path=PHASE_MATRIX,
            rtdl_fresh_path=RTDL_FRESH,
            rtdl_warm_path=RTDL_WARM,
            date="2026-07-09",
        )

        self.assertTrue(artifact["matched"])
        self.assertEqual(
            artifact["status"],
            "figure5_graphics_dragon_happy_value_matched_candidate_ready__ratio_not_authorized",
        )
        self.assertEqual(artifact["candidate"]["pair"], ["dragon.ply", "happy_buddha.ply"])
        self.assertEqual(artifact["candidate"]["level"], "level_b_same_source_candidate_only")
        self.assertFalse(artifact["candidate"]["exact_paper_dataset_identity_proven"])

    def test_artifact_records_value_match_without_claiming_exact_inputs(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        value = payload["value_evidence"]

        self.assertAlmostEqual(value["paper_log_hd_result"], 0.12572969496250153)
        self.assertAlmostEqual(value["author_rerun_hd_result"], 0.12572988867759705)
        self.assertAlmostEqual(value["rtdl_fresh_hd_result"], 0.12572988629271128)
        self.assertLess(value["author_rerun_vs_paper_log_abs_diff"], 1e-6)
        self.assertLess(value["rtdl_fresh_vs_author_rerun_abs_diff"], 1e-6)
        self.assertTrue(value["value_matched_candidate"])
        self.assertIn("does not prove byte-identical", value["paper_log_match_note"])

    def test_denominators_are_separated_and_ratio_is_forbidden(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        policy = payload["comparison_policy"]
        denominators = payload["separated_denominators"]

        self.assertFalse(policy["same_denominator_ratio_allowed"])
        self.assertFalse(policy["ratio_reported"])
        self.assertIn("paper log uses author internal timing on RTX 3090", policy["forbidden_ratio_reasons"])
        self.assertIn("RTDL reports route/case/load totals with different phase boundaries", policy["forbidden_ratio_reasons"])
        self.assertEqual(denominators["paper_log"]["record_count"], 5)
        self.assertEqual(denominators["author_rerun"]["gpu"], "NVIDIA RTX 4000 Ada Generation")
        self.assertAlmostEqual(denominators["rtdl_goal5212_fresh_route"]["route_wall_sec"], 0.8517371863126755)
        self.assertAlmostEqual(denominators["rtdl_goal5212_explicit_warm_route"]["route_wall_sec"], 0.2880803421139717)
        self.assertFalse(denominators["rtdl_goal5212_fresh_route"]["per_source_witness_exact"])

    def test_claim_boundary_allows_only_level_b_candidate(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        decision = payload["decision"]

        self.assertTrue(boundary["level_b_same_source_value_matched_candidate_claimed"])
        self.assertFalse(boundary["figure5_reproduced"])
        self.assertFalse(boundary["figure5_full_matrix_reproduced"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(decision["continue_to_ratio"])
        self.assertFalse(decision["continue_to_full_figure5_claim"])


if __name__ == "__main__":
    unittest.main()
