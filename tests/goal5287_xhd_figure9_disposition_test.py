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
    / "build_xhd_figure9_disposition.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5287_figure9_disposition_2026-07-09.json"
)
AUTO_TUNE_MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json"
)
SOURCE_AUDIT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5285_figure9_source_script_audit_2026-07-09.json"
)
BRANCH_AUDIT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json"
)


def _load_script():
    spec = importlib.util.spec_from_file_location("build_xhd_figure9_disposition", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT.parent))
    spec.loader.exec_module(module)
    return module


class Goal5287XhdFigure9DispositionTest(unittest.TestCase):
    def test_builder_closes_current_figure9_line_without_ratio(self):
        module = _load_script()
        artifact = module.build_figure9_disposition(
            auto_tune_matrix_path=AUTO_TUNE_MATRIX,
            source_audit_path=SOURCE_AUDIT,
            branch_audit_path=BRANCH_AUDIT,
            date="2026-07-09",
        )

        self.assertEqual(
            artifact["status"],
            "figure9_closed_current_line_author_denominator_missing",
        )
        self.assertTrue(artifact["matched"])
        self.assertTrue(artifact["decision"]["close_current_figure9_line"])
        self.assertFalse(artifact["decision"]["figure9_reproduced"])
        for value in artifact["claim_boundary"].values():
            self.assertFalse(value)

    def test_artifact_records_missing_denominator_and_reopen_conditions(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        evidence = payload["evidence_summary"]
        decision = payload["decision"]

        self.assertEqual(evidence["auto_tune_records"], 1814)
        self.assertEqual(evidence["auto_tune_unique_pairs"], 907)
        self.assertEqual(
            evidence["run_all_observed_configs"],
            [
                "n_points_cell_false_max_hit_false",
                "n_points_cell_true_max_hit_true",
            ],
        )
        self.assertEqual(
            evidence["missing_plot_variants"],
            [
                "n_points_cell_true_max_hit_false",
                "n_points_cell_false_max_hit_true",
            ],
        )
        self.assertEqual(evidence["main_run_all_records"], 0)
        self.assertEqual(evidence["hybrid_run_all_records"], 0)
        self.assertTrue(evidence["training_sweeps_exist"])
        self.assertFalse(evidence["training_sweeps_same_denominator_as_plot"])
        self.assertIn("auto-tune.pdf", evidence["checked_in_pdf"]["path"])
        self.assertGreaterEqual(len(decision["allowed_reopen_conditions"]), 3)
        self.assertIn("Regenerate or recover", decision["allowed_reopen_conditions"][0])

    def test_forbidden_claims_are_explicit(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        forbidden = payload["decision"]["forbidden_summaries"]
        self.assertIn("Figure 9 reproduced", forbidden)
        self.assertIn("all auto-tune variants recovered", forbidden)
        self.assertIn("checked-in PDF equals reproducible Figure 9", forbidden)
        self.assertIn("training sweep equals Figure 9", forbidden)
        self.assertIn("RTDL Figure 9 speedup or parity", forbidden)


if __name__ == "__main__":
    unittest.main()
