from __future__ import annotations

import inspect
import json
from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4164_rt_dbscan_all_predicate_only_mode_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4164_all_predicate_only_mode_pod.json"


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
            "accepted with pod evidence",
            "goal4164_all_predicate_only_mode_pod.json",
            "`all_predicate_fast_path_required`",
            "`mixed_predicate_fallback_route`",
            "does not promote the predicate direct-status route",
            "No release or public speedup claim is authorized",
        ):
            self.assertIn(fragment, report)

    def test_pod_artifact_proves_success_and_fail_closed_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal4164")
        self.assertEqual(artifact["commit"], "d25eff118d8590068c5aa0ead9c557240ae3a06c")
        self.assertIn("RTX 4000 Ada", artifact["gpu"])
        self.assertTrue(artifact["accepted"])
        self.assertEqual(
            artifact["mode"],
            "optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d",
        )
        self.assertEqual(
            artifact["acceptance"],
            {
                "all_true_observed_fast_path": True,
                "all_true_success": True,
                "mixed_failed_closed": True,
            },
        )
        all_true, mixed = artifact["cases"]
        self.assertEqual(all_true["status"], "success")
        self.assertTrue(all_true["metadata"]["all_predicate_only_mode"])
        self.assertTrue(all_true["metadata"]["all_predicate_fast_path_required"])
        self.assertTrue(all_true["metadata"]["all_predicate_fast_path_observed"])
        self.assertEqual(all_true["metadata"]["border_assignment_policy"], "not_needed_all_predicate_true")
        self.assertFalse(all_true["metadata"]["hidden_dispatch_allowed"])
        self.assertFalse(all_true["metadata"]["route_promotion_authorized"])
        self.assertFalse(all_true["metadata"]["release_authorized"])
        self.assertFalse(all_true["metadata"]["public_speedup_claim_authorized"])
        self.assertEqual(mixed["status"], "error")
        self.assertEqual(mixed["error_type"], "ValueError")
        self.assertIn("requires all_predicate_fast_path", mixed["error_message"])
        self.assertIn(app.RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE, mixed["error_message"])
        self.assertFalse(artifact["claim_boundary"]["release_authorized"])
        self.assertFalse(artifact["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["route_promotion_authorized"])
        self.assertFalse(artifact["claim_boundary"]["whole_app_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
