from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
SPEC = importlib.util.spec_from_file_location(
    "librts_figure6_denominator_audit",
    APP / "audit_exact_figure6_point_contains_denominator.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5484LibrtsExactFigure6DenominatorAuditTest(unittest.TestCase):
    def test_equal_counts_do_not_establish_equal_pointwise_relations(self):
        author_rows = {(0, 100), (1, 101)}
        rtdl_rows = {(0, 101), (1, 100)}
        self.assertEqual(len(author_rows), len(rtdl_rows))
        self.assertNotEqual(author_rows, rtdl_rows)

    def test_selects_exactly_the_six_figure6_rtspatial_100k_records(self):
        records = []
        for case_id, dataset in MODULE.CASE_DATASETS.items():
            records.append(
                {
                    "paper_figure": 6,
                    "category": "point-contains_queries_100000",
                    "index_type": "rtspatial",
                    "dataset": dataset,
                    "path": f"logs/{dataset}",
                    "loaded_geometries": 1,
                    "loaded_queries": 100000,
                    "loading_ms": 1.0,
                    "query_ms": 0.1,
                    "result_count": 2,
                }
            )
        records.append(
            {
                "paper_figure": 6,
                "category": "point-contains_queries_100000",
                "index_type": "cgal",
                "dataset": "dtl_cnty.wkt.log",
            }
        )
        selected = MODULE.select_figure6_rtspatial_records({"records": records})
        self.assertEqual(set(selected), set(MODULE.CASE_DATASETS))

    def test_build_audit_rejects_count_or_input_mismatch(self):
        records = [
            {
                "paper_figure": 6,
                "category": "point-contains_queries_100000",
                "index_type": "rtspatial",
                "dataset": dataset,
                "path": f"logs/{dataset}",
                "loaded_geometries": 1,
                "loaded_queries": 100000,
                "loading_ms": 1.0,
                "query_ms": 0.1,
                "result_count": 2,
            }
            for dataset in MODULE.CASE_DATASETS.values()
        ]
        case = {
            "matched": True,
            "author": {"geometry_count": 1, "query_count": 100000, "result_count": 2},
            "input_identity": {"same_files_passed_to_author_and_rtdl": True},
        }
        remaining = {"cases": {case_id: dict(case) for case_id in MODULE.CASE_DATASETS if case_id != "dtl_cnty"}}
        remaining["cases"]["parks.bz2"]["author"]["result_count"] = 3
        with self.assertRaises(ValueError):
            MODULE.build_audit(
                author_logs={"records": records},
                first=case,
                remaining=remaining,
            )

    def test_audit_keeps_performance_ratio_closed(self):
        records = [
            {
                "paper_figure": 6,
                "category": "point-contains_queries_100000",
                "index_type": "rtspatial",
                "dataset": dataset,
                "path": f"logs/{dataset}",
                "loaded_geometries": 1,
                "loaded_queries": 100000,
                "loading_ms": 1.0,
                "query_ms": 0.1,
                "result_count": 2,
            }
            for dataset in MODULE.CASE_DATASETS.values()
        ]
        case = {
            "matched": True,
            "author": {"geometry_count": 1, "query_count": 100000, "result_count": 2},
            "input_identity": {"same_files_passed_to_author_and_rtdl": True},
        }
        remaining = {"cases": {case_id: dict(case) for case_id in MODULE.CASE_DATASETS if case_id != "dtl_cnty"}}
        audit = MODULE.build_audit(
            author_logs={"records": records},
            first=case,
            remaining=remaining,
        )
        self.assertTrue(audit["all_cases_aligned"])
        self.assertFalse(audit["phase_boundary"]["performance_ratio_authorized"])
        self.assertFalse(audit["claim_boundary"]["figure6_reproduced"])


if __name__ == "__main__":
    unittest.main()
