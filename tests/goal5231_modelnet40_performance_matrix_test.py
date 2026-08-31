from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_modelnet40_performance_matrix.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("build_xhd_modelnet40_performance_matrix_goal5231", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _case(index: int, category: str, *, matched: bool = True) -> dict[str, object]:
    return {
        "case_index": index,
        "case_name": f"{index:04d}_{category}_a__{category}_b",
        "category": category,
        "case_matched": matched,
        "total_points": 100 + index,
        "author_normalized": {
            "running_avg_time_ms": 10.0 + index,
            "process_wall_sec": 0.5 + index,
        },
        "rtdl_normalized_route": {
            "route_wall_sec": 1.0 + index,
            "total_sec": 2.0 + index,
            "author_abs_diff": 1e-8 * (index + 1),
        },
    }


class Goal5231ModelNet40PerformanceMatrixTest(unittest.TestCase):
    def test_matrix_preserves_denominator_boundaries_and_record_coverage(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unique_summary = root / "unique_summary.json"
            record_coverage = root / "record_coverage.json"
            unique_summary.write_text(
                json.dumps({"all_cases_matched": True, "cases": [_case(0, "chair"), _case(1, "table")]}),
                encoding="utf-8",
            )
            record_coverage.write_text(
                json.dumps(
                    {
                        "record_count": 10,
                        "covered_record_count": 10,
                        "all_records_covered": True,
                        "algorithm_distribution": {"Hybrid": 5, "Ray Tracing": 5},
                    }
                ),
                encoding="utf-8",
            )

            summary = module.build_summary(
                argparse.Namespace(
                    unique_summary=unique_summary,
                    record_coverage=record_coverage,
                    goal_label="Goal5231",
                )
            )

        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.modelnet40_performance_matrix.v1")
        self.assertEqual(summary["case_count"], 2)
        self.assertTrue(summary["record_coverage_summary"]["all_records_covered"])
        self.assertAlmostEqual(summary["timing_scopes"]["author_internal_avg_time_sec"]["stats"]["sum"], 0.021)
        self.assertEqual(summary["timing_scopes"]["author_process_wall_sec"]["stats"]["sum"], 2.0)
        self.assertEqual(summary["timing_scopes"]["rtdl_route_wall_sec"]["stats"]["sum"], 3.0)
        self.assertEqual(summary["timing_scopes"]["rtdl_full_total_sec"]["stats"]["sum"], 5.0)
        self.assertEqual(summary["diagnostic_ratios"]["rtdl_route_sum_over_author_process_wall_sum"], 1.5)
        self.assertFalse(summary["diagnostic_ratios"]["ratios_are_authorized_performance_claims"])
        self.assertFalse(summary["claim_boundary"]["author_vs_rtdl_speedup_claimed"])
        self.assertFalse(summary["claim_boundary"]["author_vs_rtdl_parity_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_xhd_paper_reproduction_claimed"])
        self.assertEqual(set(summary["by_category"]), {"chair", "table"})

    def test_matrix_rejects_unmatched_unique_cases(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            unique_summary = Path(tmp) / "unique_summary.json"
            unique_summary.write_text(json.dumps({"cases": [_case(0, "chair", matched=False)]}), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "requires matched cases"):
                module.build_summary(
                    argparse.Namespace(
                        unique_summary=unique_summary,
                        record_coverage=None,
                        goal_label="Goal5231",
                    )
                )

    def test_script_remains_app_owned_not_core_performance_primitive(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("denominator-explicit", source)
        self.assertIn("ratios_are_authorized_performance_claims", source)
        for forbidden in ("rtdsl.modelnet", "rtdsl.xhd", "native_modelnet", "native_xhd"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
