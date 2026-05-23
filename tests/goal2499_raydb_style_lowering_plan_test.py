from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2499_raydb_style_lowering_gap_and_next_engine_target_2026-05-22.md"
GENERIC_SOURCE = ROOT / "src/rtdsl/columnar_aggregate_reference.py"


class Goal2499RaydbStyleLoweringPlanTest(unittest.TestCase):
    def test_cpu_lowering_plan_supports_all_reference_modes(self) -> None:
        plan = rt.plan_columnar_aggregate_lowering("cpu_python_reference")
        self.assertIsInstance(plan, rt.ColumnarAggregateLoweringPlan)
        self.assertEqual(plan.supported_aggregates, rt.SUPPORTED_AGGREGATES)
        self.assertFalse(plan.uses_compatibility_wrapper)
        self.assertFalse(plan.materializes_input_rows_for_wrapper)
        self.assertTrue(plan.direct_columnar_record_set_api)
        self.assertFalse(plan.true_zero_copy_authorized)
        self.assertFalse(plan.requires_runtime_validation)

    def test_native_lowering_plans_are_count_sum_direct_columnar_paths(self) -> None:
        self.assertEqual(rt.NATIVE_COLUMNAR_COUNT_SUM_BACKENDS, ("embree", "optix"))
        for backend in rt.NATIVE_COLUMNAR_COUNT_SUM_BACKENDS:
            with self.subTest(backend=backend):
                plan = rt.plan_columnar_aggregate_lowering(backend)
                self.assertEqual(plan.supported_aggregates, ("count", "sum"))
                self.assertEqual(plan.unsupported_aggregates, ("min", "max", "avg_as_sum_count"))
                self.assertEqual(plan.transfer_path, "direct_columnar_record_set_to_columnar_payload")
                self.assertFalse(plan.uses_compatibility_wrapper)
                self.assertFalse(plan.materializes_input_rows_for_wrapper)
                self.assertTrue(plan.direct_columnar_record_set_api)
                self.assertFalse(plan.true_zero_copy_authorized)
                self.assertTrue(plan.requires_runtime_validation)
                self.assertEqual(
                    plan.next_engine_target,
                    "optix_partner_resident_columnar_payload_native_execution",
                )

    def test_app_metadata_carries_lowering_plan(self) -> None:
        payload = app.run_result_mode("count")
        lowering_plan = payload["metadata"]["lowering_plan"]
        self.assertEqual(lowering_plan["backend"], "cpu_python_reference")
        self.assertEqual(lowering_plan["supported_aggregates"], list(rt.SUPPORTED_AGGREGATES))
        self.assertFalse(lowering_plan["true_zero_copy_authorized"])

    def test_unknown_backend_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported columnar aggregate lowering backend"):
            rt.plan_columnar_aggregate_lowering("custom_backend")

    def test_generic_lowering_source_avoids_app_vocabulary(self) -> None:
        source = GENERIC_SOURCE.read_text(encoding="utf-8").lower()
        for forbidden in ("raydb", "sql", "database", "ssb"):
            self.assertNotIn(forbidden, source)

    def test_report_records_next_engine_target_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("direct_columnar_record_set_preparation_without_row_mapping", text)
        self.assertIn("not the final engine shape", text)
        self.assertIn("true zero-copy wording", text)
        self.assertIn("new app-specific native ABI", text)


if __name__ == "__main__":
    unittest.main()
