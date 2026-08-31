import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_figure9_source_audit.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5285_figure9_source_script_audit_2026-07-09.json"
)


class Goal5285XhdFigure9SourceScriptAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ARTIFACT.exists():
            raise unittest.SkipTest(f"missing artifact: {ARTIFACT}")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_keeps_figure9_unreproduced_boundary(self):
        payload = self.payload

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.figure9_source_script_audit.v1",
        )
        self.assertEqual(payload["goal"], "Goal5285")
        self.assertEqual(
            payload["status"],
            "figure9_plot_script_expects_missing_run_all_variants__figure9_not_reproduced",
        )
        self.assertFalse(payload["decision"]["figure9_reproduced"])
        self.assertFalse(payload["claim_boundary"]["figure9_reproduced"])
        self.assertFalse(payload["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["rtdl_route_result_claimed"])
        self.assertIn("Figure 9 reproduced", payload["decision"]["forbidden_summaries"])
        self.assertIn("training sweep equals Figure 9", payload["decision"]["forbidden_summaries"])

    def test_plot_script_expects_four_variants_but_run_all_has_two(self):
        payload = self.payload
        expected = payload["figure9_plot_script"]["expected_variants"]
        observed = payload["run_all_vs_plot_script"]["observed_configs"]
        missing = payload["run_all_vs_plot_script"]["missing_plot_variants_from_run_all_logs"]

        self.assertTrue(payload["figure9_plot_script"]["exists"])
        self.assertTrue(payload["figure9_plot_script"]["active_draw_call_in_source_tail"])
        self.assertTrue(payload["figure9_plot_script"]["loads_run_all_auto_tune"])
        self.assertTrue(payload["figure9_plot_script"]["saves_pdf"])
        self.assertEqual(
            expected,
            [
                "n_points_cell_false_max_hit_false",
                "n_points_cell_true_max_hit_false",
                "n_points_cell_false_max_hit_true",
                "n_points_cell_true_max_hit_true",
            ],
        )
        self.assertEqual(
            observed,
            [
                "n_points_cell_false_max_hit_false",
                "n_points_cell_true_max_hit_true",
            ],
        )
        self.assertEqual(
            missing,
            [
                "n_points_cell_true_max_hit_false",
                "n_points_cell_false_max_hit_true",
            ],
        )
        self.assertFalse(
            payload["run_all_vs_plot_script"]["all_plot_variants_present_in_current_run_all_logs"]
        )
        self.assertEqual(payload["run_all_auto_tune_logs"]["record_count"], 1814)
        self.assertEqual(payload["run_all_auto_tune_logs"]["unique_pair_count"], 907)
        self.assertEqual(payload["run_all_auto_tune_logs"]["complete_two_config_pair_count"], 907)

    def test_training_sweeps_are_separate_from_figure9_run_all(self):
        payload = self.payload
        sweeps = payload["training_sweeps"]
        flags = payload["source_flags_and_models"]

        self.assertTrue(sweeps["not_same_as_figure9_run_all"])
        self.assertEqual(sweeps["script_n_points_cell_list"], [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80])
        self.assertEqual(sweeps["script_max_hit_list"], [1, 16, 32, 64, 128, 256, 512])
        self.assertEqual(sweeps["logs"]["n_points_cell_value_count"], 30)
        self.assertEqual(sweeps["logs"]["n_points_cell_values"], list(range(1, 31)))
        self.assertIn("logs/train", sweeps["reason"])
        self.assertIn("logs/run_all/auto_tune", sweeps["reason"])

        self.assertTrue(flags["has_auto_tune_flag"])
        self.assertTrue(flags["has_auto_tune_n_points_cell_flag"])
        self.assertTrue(flags["has_auto_tune_max_hit_flag"])
        self.assertTrue(flags["has_n_points_cell_list_flag"])
        self.assertTrue(flags["has_max_hit_list_flag"])
        self.assertTrue(flags["hybrid_predicts_num_points_per_cell"])
        self.assertTrue(flags["hybrid_predicts_max_hit"])

    def test_script_is_app_owned_and_does_not_import_rtdl_route_code(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("does not run an\nRTDL route", source)
        self.assertNotIn("src.rtdsl", source)
        self.assertNotIn("rtdsl.", source)
        self.assertNotIn("run_xhd", source)


if __name__ == "__main__":
    unittest.main()
