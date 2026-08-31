import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_SOURCE = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT_SOURCE = REPO_ROOT / "src" / "rtdsl" / "__init__.py"
APP_SOURCE = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_distance_app.py"
)
GOAL3143_TEST = REPO_ROOT / "tests" / "goal3143_hausdorff_partner_exact_numba_front_door_test.py"
GOAL3160_TEST = REPO_ROOT / "tests" / "goal3160_hausdorff_generic_max_nearest_front_door_alias_test.py"
FUTURE_TODO = REPO_ROOT / "docs" / "research" / "future_version_to_do_list.md"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3788_hausdorff_generic_alias_and_metadata_audit_2026-06-07.md"


class Goal3788HausdorffGenericAliasAndMetadataAuditTest(unittest.TestCase):
    def test_generic_alias_is_already_primary_and_compatibility_adapter_remains(self) -> None:
        adapter = ADAPTER_SOURCE.read_text(encoding="utf-8")
        init_text = INIT_SOURCE.read_text(encoding="utf-8")
        app = APP_SOURCE.read_text(encoding="utf-8")

        self.assertIn("def directed_max_of_nearest_distance_2d_partner_columns", adapter)
        self.assertIn("def directed_hausdorff_2d_partner_columns", adapter)
        self.assertIn("compatibility_adapter_aliases", adapter)
        self.assertIn("generic_directed_max_of_nearest_distance_2d", adapter)
        self.assertIn("from .partner_adapters import directed_max_of_nearest_distance_2d_partner_columns", init_text)
        self.assertIn('"directed_max_of_nearest_distance_2d_partner_columns"', init_text)

        helper_start = app.index("def _run_partner_exact_directed")
        helper_end = app.index("def _run_partner_numpy_exact_directed", helper_start)
        helper = app[helper_start:helper_end]
        self.assertIn("rt.directed_max_of_nearest_distance_2d_partner_columns", helper)
        self.assertNotIn("rt.directed_hausdorff_2d_partner_columns", helper)

    def test_numba_metadata_reports_only_executed_sqrt_operation(self) -> None:
        adapter = ADAPTER_SOURCE.read_text(encoding="utf-8")
        numba_start = adapter.index("def _directed_hausdorff_2d_numba_partner_columns")
        compat_start = adapter.index("def directed_hausdorff_2d_partner_columns", numba_start)
        numba_impl = adapter[numba_start:compat_start]

        self.assertIn('executed_operations = [score_operation, "grouped_argmin_f64", "grouped_argmax_f64"]', numba_impl)
        self.assertIn('if sqrt_result is not None:\n        executed_operations.append("sqrt_f64")', numba_impl)
        self.assertIn('"v2_8_partner_continuation_operations": tuple(executed_operations)', numba_impl)
        self.assertIn('"v2_8_partner_continuation_operations_semantics": "executed_operations_this_call"', numba_impl)
        self.assertIn('"nearest_distance_column_materialized": sqrt_result is not None', numba_impl)

    def test_existing_goal_tests_cover_the_old_review_findings(self) -> None:
        goal3143 = GOAL3143_TEST.read_text(encoding="utf-8")
        goal3160 = GOAL3160_TEST.read_text(encoding="utf-8")

        self.assertIn('self.assertNotIn("sqrt_f64", payload["directed_a_to_b"]["v2_8_partner_continuation_operations"])', goal3143)
        self.assertIn("directed_max_of_nearest_distance_2d_partner_columns", goal3160)
        self.assertIn('self.assertEqual(metadata["adapter"], "directed_max_of_nearest_distance_2d_partner_columns")', goal3160)
        self.assertIn('self.assertFalse(metadata["nearest_distance_column_materialized"])', goal3160)

    def test_stale_future_todo_item_was_removed_and_report_is_bounded(self) -> None:
        todo = FUTURE_TODO.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertNotIn("## Generic Adapter Naming", todo)
        self.assertIn("Goal3788 Hausdorff Generic Alias And Metadata Audit", report)
        for phrase in (
            "Status: implemented and pod-validated",
            "No runtime code or native code was changed",
            "NVIDIA RTX A5000",
            "Numba CUDA available: True",
            "does not authorize release action",
            "automatic partner selection",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
