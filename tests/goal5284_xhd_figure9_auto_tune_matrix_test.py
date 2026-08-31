import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_figure9_auto_tune_matrix.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_xhd_figure9_auto_tune_matrix", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _record(pair, config, *, category="graphics", avg=1.0, hd=0.5):
    a, b = pair
    return {
        "section": "auto_tune",
        "category": category,
        "config": config,
        "relative_log_path": f"expr/for_the_paper/logs/run_all/auto_tune/{category}/{config}/{a}_{b}.json",
        "hd_result": hd,
        "input": {
            "num_dims": 3,
            "files": [
                {"basename": a, "num_points": 10},
                {"basename": b, "num_points": 12},
            ],
        },
        "running": {
            "avg_time": avg,
            "reported_time_median": avg,
            "num_points_per_cell": 8,
            "seed": 0,
            "eb": None,
            "prune": None,
            "lb": None,
        },
    }


class Goal5284XhdFigure9AutoTuneMatrixTest(unittest.TestCase):
    def test_build_matrix_classifies_auto_tune_logs_without_figure_claim(self):
        module = _load_module()
        log_index = {
            "goal": "Goal5176",
            "author_repo": {"head": "paper-branch-fixture"},
            "run_all_records": [
                _record(
                    ("dragon.ply", "asian_dragon.ply"),
                    "n_points_cell_false_max_hit_false",
                    avg=10.0,
                ),
                _record(
                    ("dragon.ply", "asian_dragon.ply"),
                    "n_points_cell_true_max_hit_true",
                    avg=8.0,
                ),
                _record(
                    ("dragon.ply", "happy_buddha.ply"),
                    "n_points_cell_false_max_hit_false",
                    avg=5.0,
                ),
                _record(
                    ("dragon.ply", "happy_buddha.ply"),
                    "n_points_cell_true_max_hit_true",
                    avg=6.0,
                ),
            ],
        }

        payload = module.build_matrix(log_index, max_examples=4)

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.figure9_auto_tune_semantics.v1",
        )
        self.assertEqual(payload["coverage"]["auto_tune_record_count"], 4)
        self.assertEqual(payload["coverage"]["unique_pair_count"], 2)
        self.assertEqual(payload["coverage"]["complete_pair_count_with_both_observed_configs"], 2)
        self.assertEqual(payload["coverage"]["incomplete_pair_count"], 0)
        self.assertEqual(
            payload["observed_config_semantics"]["all_running_num_points_per_cell_values"],
            [8],
        )
        self.assertFalse(
            payload["observed_config_semantics"]["grid_size_sweep_present_in_run_all_auto_tune_logs"]
        )
        self.assertEqual(payload["config_pair_comparison"]["hd_result_mismatch_pair_count"], 0)
        self.assertEqual(
            payload["config_pair_comparison"]["winner_counts_by_avg_time"],
            {
                "n_points_cell_false_max_hit_false": 1,
                "n_points_cell_true_max_hit_true": 1,
            },
        )
        self.assertFalse(payload["figure9_reproduction_decision"]["figure9_reproduced"])
        self.assertIn(
            "full adaptive-grid parameter sweep semantics",
            payload["figure9_reproduction_decision"]["what_is_missing"],
        )
        self.assertFalse(payload["claim_boundary"]["figure9_reproduced"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])

    def test_real_artifact_records_author_log_mapping_not_figure_reproduction(self):
        if not ARTIFACT.exists():
            self.skipTest(f"missing artifact: {ARTIFACT}")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["status"],
            "figure9_auto_tune_mapping_ready__figure9_not_reproduced",
        )
        self.assertEqual(payload["coverage"]["auto_tune_record_count"], 1814)
        self.assertEqual(payload["coverage"]["unique_pair_count"], 907)
        self.assertEqual(payload["coverage"]["complete_pair_count_with_both_observed_configs"], 907)
        self.assertEqual(payload["coverage"]["incomplete_pair_count"], 0)
        self.assertEqual(
            payload["coverage"]["configs"],
            {
                "n_points_cell_false_max_hit_false": 907,
                "n_points_cell_true_max_hit_true": 907,
            },
        )
        self.assertEqual(
            payload["observed_config_semantics"]["all_running_num_points_per_cell_values"],
            [8],
        )
        self.assertFalse(
            payload["observed_config_semantics"]["grid_size_sweep_present_in_run_all_auto_tune_logs"]
        )
        self.assertEqual(payload["config_pair_comparison"]["hd_result_mismatch_pair_count"], 0)
        self.assertGreater(
            payload["config_pair_comparison"]["winner_counts_by_avg_time"][
                "n_points_cell_true_max_hit_true"
            ],
            payload["config_pair_comparison"]["winner_counts_by_avg_time"][
                "n_points_cell_false_max_hit_false"
            ],
        )
        self.assertFalse(payload["figure9_reproduction_decision"]["figure9_reproduced"])
        self.assertFalse(payload["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["rtdl_route_result_claimed"])


if __name__ == "__main__":
    unittest.main()
