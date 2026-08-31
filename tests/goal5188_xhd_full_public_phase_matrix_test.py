from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_full_public_phase_matrix.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_xhd_full_public_phase_matrix", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5188XhdFullPublicPhaseMatrixTest(unittest.TestCase):
    def test_phase_matrix_separates_author_and_rtdl_denominators(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            author_summary = root / "author_summary.json"
            author_json = root / "author.json"
            rtdl_summary = root / "rtdl.json"
            author_summary.write_text(
                json.dumps(
                    {
                        "matched": True,
                        "author_hd_result": 0.125,
                        "author_running_avg_time_ms": 7.8,
                        "author_run": {"wall_sec": 0.42},
                    }
                ),
                encoding="utf-8",
            )
            author_json.write_text(
                json.dumps(
                    {
                        "Running": {
                            "AvgTime": 7.8,
                            "Repeats": [
                                {
                                    "ReportedTime": 7.8,
                                    "BVHBuildTime": 0.3,
                                    "GridResolution": [1, 2, 3],
                                    "LargeCells": 4,
                                    "Iterations": [
                                        {
                                            "Iteration": 1,
                                            "NumInputPoints": 10,
                                            "NumOutputPoints": 2,
                                            "RTTime": 3.0,
                                            "CUDATime": 1.0,
                                            "OffloadingSize": 5,
                                            "Radius": 0.1,
                                        }
                                    ],
                                }
                            ],
                        }
                    }
                ),
                encoding="utf-8",
            )
            rtdl_summary.write_text(
                json.dumps(
                    {
                        "target": "graphics_dragon_happy_buddha",
                        "full_point_counts": {"source": 10, "target": 20},
                        "input1": "a.ply",
                        "input2": "b.ply",
                        "author_tolerance": 1e-6,
                        "summary_statistics": {
                            "all_matched": True,
                            "median_route_wall_sec": 7.3,
                        },
                        "phase_timings_sec": {
                            "load_full_inputs": 2.5,
                            "total": 10.0,
                        },
                        "cases": [
                            {
                                "author_abs_diff": 2e-9,
                                "exact_oracle_used": False,
                                "phase_timings_sec": {
                                    "case_total": 7.9,
                                    "select_source_subset": 0.1,
                                },
                                "rtdl_route": {
                                    "distance": 0.125000002,
                                    "phase_timings_sec": {
                                        "initial_state_seed": 4.0,
                                        "frontier_rows": 2.0,
                                    },
                                    "frontier_row_count": 123,
                                    "frontier_row_capacity": 1000,
                                    "frontier_native_symbol": "native_generic_symbol",
                                    "initial_cell_mbr_tests": 100,
                                    "total_candidate_distance_evaluations": 50,
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            summary = module.build_summary(
                argparse.Namespace(
                    author_summary=author_summary,
                    author_json=author_json,
                    rtdl_route_summary=rtdl_summary,
                    output=root / "matrix.json",
                    run_goal="Goal5188",
                )
            )

        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.full_public_phase_matrix.v1")
        self.assertTrue(summary["correctness_anchor"]["matched"])
        self.assertFalse(summary["correctness_anchor"]["exact_oracle_used"])
        self.assertEqual(summary["author_phase_evidence"]["running_avg_time_ms"], 7.8)
        self.assertEqual(summary["author_phase_evidence"]["process_wall_sec"], 0.42)
        self.assertEqual(summary["rtdl_phase_evidence"]["route_wall_sec"], 7.3)
        self.assertEqual(summary["rtdl_phase_evidence"]["total_sec"], 10.0)
        self.assertFalse(summary["comparison_policy"]["ratio_reported"])
        self.assertFalse(summary["comparison_policy"]["author_running_avg_vs_rtdl_route_ratio_computed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()
