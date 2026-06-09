from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4176_declared_rtdbscan_all_items_direct_status_refactor_2026-06-09.md"


class Goal4176DeclaredRtDbscanAllItemsDirectStatusRefactorTest(unittest.TestCase):
    def test_declared_route_uses_generic_all_items_direct_status_handle(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("use_declared_all_predicate", source)
        self.assertIn(
            "rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(",
            source,
        )
        self.assertIn(
            "rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(",
            source,
        )
        self.assertIn(
            "rt.prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_preview_3d(",
            source,
        )

    def test_declared_route_does_not_materialize_predicate_or_neighbor_columns(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"path": "caller_declared_all_true_predicate_no_columns_3d"', source)
        self.assertIn('"columns": {}', source)
        self.assertIn('"predicate_columns_materialized": False', source)
        self.assertIn('"uses_generic_all_items_direct_status_signature": True', source)
        self.assertIn('"neighbor_count_policy": "not_materialized_all_items_declared_predicate_true"', source)
        self.assertIn(
            '"generic_all_items_direct_status_component_signature_wrapped_as_all_predicate_signature"',
            source,
        )
        self.assertNotIn('"threshold_satisfying_sentinel_not_exact_degree"', source)

    def test_declared_route_wraps_generic_component_signature_as_dbscan_signature(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("_cluster_signature_from_nonnegative_label_counts(", source)
        self.assertIn('result["columns"]["component_size_signature"]', source)
        self.assertIn("core_count=len(points)", source)
        self.assertIn("noise_count=0", source)
        self.assertIn('result_metadata["all_predicate_fast_path"] = True', source)

    def test_report_records_scope_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "implementation accepted pending pod timing",
            "No synthetic predicate columns are materialized",
            "No synthetic neighbor-count sentinel columns are materialized",
            "generic\nall-items component primitive directly",
            "app boundary",
            "Pod timing is still required",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
