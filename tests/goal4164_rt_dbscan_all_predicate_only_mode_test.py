from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4164_rt_dbscan_all_predicate_only_mode_2026-06-09.md"


class Goal4164RtDbscanAllPredicateOnlyModeTest(unittest.TestCase):
    def test_app_exposes_explicit_all_predicate_only_mode(self) -> None:
        self.assertEqual(
            app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE,
            "optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d",
        )
        advice = app.explain_rt_dbscan_explicit_route_choice(
            "clustered3d",
            repeated_component_signature=True,
            point_count=65536,
        )
        all_true_options = [
            option for option in advice["options"]
            if option["mode"] == app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE
        ]
        self.assertTrue(all_true_options)
        first = all_true_options[0]
        self.assertIs(first["all_predicate_fast_path_required"], True)
        self.assertIs(first["mixed_predicate_fail_closed"], True)
        self.assertEqual(first["mixed_predicate_fallback_route"], app.RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE)
        self.assertEqual(first["border_assignment_policy"], "not_needed_all_predicate_true")

    def test_runtime_branch_requires_runtime_fast_path_metadata(self) -> None:
        source = inspect.getsource(app.run_rt_dbscan_benchmark)
        self.assertIn("RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE", source)
        self.assertIn("require_all_predicate_fast_path = mode == RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE", source)
        self.assertIn("requires all_predicate_fast_path", source)
        self.assertIn("optix_rt_core_grouped_stream_numba_column_signature_3d for mixed predicate rows", source)
        self.assertIn('"all_predicate_only_mode": require_all_predicate_fast_path', source)
        self.assertIn('"all_predicate_fast_path_required": require_all_predicate_fast_path', source)
        self.assertIn('"all_predicate_fast_path_observed": bool(metadata.get("all_predicate_fast_path", False))', source)
        self.assertIn('"mixed_predicate_fail_closed": require_all_predicate_fast_path', source)
        self.assertIn('"route_promotion_authorized": False', source)
        self.assertIn('"hidden_dispatch_allowed": False', source)

    def test_cli_and_signature_row_guard_include_the_mode(self) -> None:
        source = (ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(
            source.count("optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d"),
            4,
        )
        self.assertIn("signature mode does not materialize Python rows", source)

    def test_report_records_non_promoted_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "all-predicate-only candidate mode",
            "fails closed on mixed predicate rows",
            "`all_predicate_fast_path_required`",
            "`mixed_predicate_fallback_route`",
            "does not promote the predicate direct-status route",
            "No release or public speedup claim is authorized",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
