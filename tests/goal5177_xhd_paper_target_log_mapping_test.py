import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "map_xhd_paper_targets_to_logs.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("map_xhd_paper_targets_to_logs", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _record(section, category, a, b, *, avg=1.0, points=(10, 12), dims=3, config=None):
    config = config or f"{a}_{b}.json"
    return {
        "section": section,
        "category": category,
        "config": config,
        "relative_log_path": f"expr/for_the_paper/logs/run_all/{section}/{category}/{config}",
        "file_name": config,
        "hd_result": 0.5,
        "input": {
            "num_dims": dims,
            "files": [
                {
                    "basename": a,
                    "num_points": points[0],
                    "exact_status": "author_log_path_known__input_file_not_available",
                },
                {
                    "basename": b,
                    "num_points": points[1],
                    "exact_status": "author_log_path_known__input_file_not_available",
                },
            ],
        },
        "running": {
            "avg_time": avg,
            "reported_time_median": avg,
            "num_points_per_cell": 8,
        },
    }


class Goal5177PaperTargetLogMappingTest(unittest.TestCase):
    def test_mapping_separates_log_coverage_from_figure_reproduction_claims(self):
        module = _load_module()
        log_index = {
            "goal": "Goal5176",
            "author_repo": {"head": "paper-branch-fixture"},
            "run_all_records": [
                _record("rt_gpu", "graphics", "dragon.ply", "asian_dragon.ply"),
                _record("eb_gpu", "graphics", "dragon.ply", "asian_dragon.ply"),
                _record("hybrid_gpu", "graphics", "dragon.ply", "happy_buddha.ply"),
                _record(
                    "rt_gpu",
                    "geo",
                    "lakes.bz2.wkt",
                    "parks.bz2.wkt",
                    dims=2,
                    points=(100, 200),
                ),
                _record(
                    "rt_gpu",
                    "geo",
                    "dtl_cnty.wkt",
                    "uszipcode.wkt",
                    dims=2,
                    points=(30, 40),
                ),
                _record(
                    "auto_tune",
                    "BraTS2020_ValidationData",
                    "BraTS20_Validation_001_flair.nii",
                    "BraTS20_Validation_033_flair.nii",
                    config="n_points_cell_false_max_hit_false",
                ),
            ],
        }
        target_matrix = {
            "goal": "Goal5130",
            "status": "xhd_paper_target_matrix_ready",
        }

        mapping = module.build_mapping(target_matrix, log_index, max_examples=3)

        self.assertEqual(
            mapping["schema"],
            "rtdl.paper_reproduction.xhd.paper_target_log_mapping.v1",
        )
        self.assertEqual(mapping["run_all_summary"]["record_count"], 6)
        self.assertFalse(mapping["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(mapping["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(mapping["claim_boundary"]["figure_reproduction_claimed"])
        self.assertTrue(
            mapping["exact_dataset_rule"]["statistics_matching_is_not_exact_identity"]
        )

        by_figure = {row["figure"]: row for row in mapping["figure_mappings"]}
        self.assertEqual(
            by_figure["Figure 5"]["coverage_status"],
            "run_all_timing_logs_cover_required_workload_families__inputs_missing",
        )
        self.assertIn("input file bytes and hashes", by_figure["Figure 5"]["missing_evidence"])
        self.assertEqual(
            by_figure["Figure 6"]["coverage_status"],
            "partially_covered_by_run_all_timing_logs__phase_counters_missing",
        )
        self.assertIn("intersection counts", by_figure["Figure 6"]["missing_evidence"])
        self.assertEqual(
            by_figure["Figure 11"]["coverage_status"],
            "not_covered_by_run_all_timing_logs",
        )

        subsets = {row["name"]: row for row in mapping["priority_subsets"]}
        self.assertGreater(
            subsets["graphics_dragon_asian_dragon"]["record_summary"]["record_count"],
            0,
        )
        self.assertEqual(
            subsets["graphics_dragon_asian_dragon"]["status"],
            "paper_log_workload_identified__input_files_missing",
        )
        self.assertIn(
            "Level B",
            subsets["graphics_dragon_asian_dragon"]["authorized_next_step"],
        )


if __name__ == "__main__":
    unittest.main()
