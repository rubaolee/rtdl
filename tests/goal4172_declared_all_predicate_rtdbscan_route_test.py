from __future__ import annotations

from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4172_declared_all_predicate_rtdbscan_route_2026-06-09.md"


class Goal4172DeclaredAllPredicateRtDbscanRouteTest(unittest.TestCase):
    def test_mode_is_explicit_and_cli_visible(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn(
            'RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE = (',
            source,
        )
        self.assertIn(
            '"partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d"',
            source,
        )
        self.assertIn("use_declared_all_predicate = mode == RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE", source)
        self.assertIn("nullcontext(None)", source)

    def test_declared_route_skips_count_threshold_and_records_external_proof_boundary(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"predicate_flags_source": "caller_declared_all_true"', source)
        self.assertIn('"predicate_flags_exactness": "caller_asserted_not_rt_count_threshold_verified"', source)
        self.assertIn('"rt_count_threshold_executed": False', source)
        self.assertIn('"optix_backend_used_for_threshold": False', source)
        self.assertIn('"caller_declared_predicate_columns_require_external_proof": use_declared_all_predicate', source)
        self.assertIn('"neighbor_count_policy": "not_materialized_all_items_declared_predicate_true"', source)
        self.assertIn('"predicate_columns_materialized": False', source)
        self.assertIn('"uses_generic_all_items_direct_status_signature": True', source)

    def test_declared_route_does_not_claim_rt_core_acceleration_or_promotion(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"optix_backend_used": not use_declared_all_predicate', source)
        self.assertIn('"rt_core_accelerated": not use_declared_all_predicate', source)
        self.assertIn('"route_promotion_authorized": False', source)
        self.assertIn('"hidden_dispatch_allowed": False', source)
        self.assertIn('"predicate_direct_status_promoted": False', source)

    def test_advisor_exposes_declared_route_without_promoting_it(self) -> None:
        advice = app.explain_rt_dbscan_explicit_route_choice(
            "road3d",
            repeated_component_signature=False,
            point_count=2_097_152,
        )
        declared_options = [
            option
            for option in advice["options"]
            if option["mode"] == app.RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE
        ]
        self.assertTrue(declared_options)
        first_declared = declared_options[0]
        self.assertEqual(first_declared["predicate_flags_source"], "caller_declared_all_true")
        self.assertTrue(first_declared["caller_declared_predicate_columns_require_external_proof"])
        self.assertFalse(first_declared["rt_count_threshold_executed"])
        self.assertFalse(first_declared["rt_core_acceleration_claim_authorized"])
        self.assertFalse(first_declared["automatic_route_selection_authorized"])
        self.assertFalse(first_declared["route_promotion_authorized"])
        self.assertNotEqual(advice["options"][0]["mode"], app.RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE)

    def test_report_records_scope_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "implementation accepted pending pod timing",
            "caller-declared all-predicate route",
            "explicit external-proof option",
            "No RT-count-threshold execution",
            "No RT-core acceleration claim",
            "all-true predicate precondition",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
