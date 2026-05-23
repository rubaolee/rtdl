import json
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2503_direct_columnar_record_set_preparation_2026-05-22.md"
APP = ROOT / "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py"
POD_APP = ROOT / "docs/reports/goal2503_direct_columnar_optix_app_pod_2026-05-22.json"
POD_MATRIX = ROOT / "docs/reports/goal2503_direct_columnar_optix_backend_matrix_pod_2026-05-22.json"


def _require_embree() -> None:
    try:
        rt.embree_version()
    except Exception as exc:
        raise unittest.SkipTest(f"Embree backend unavailable: {exc}") from exc


def _require_optix() -> None:
    try:
        rt.optix_version()
    except Exception as exc:
        raise unittest.SkipTest(f"OptiX backend unavailable: {exc}") from exc


class Goal2503DirectColumnarRecordSetPreparationTest(unittest.TestCase):
    def test_public_direct_preparation_apis_are_exported(self) -> None:
        self.assertTrue(hasattr(rt, "prepare_embree_columnar_record_set"))
        self.assertTrue(hasattr(rt, "prepare_optix_columnar_record_set"))

    def test_native_lowering_plan_no_longer_materializes_row_mappings(self) -> None:
        for backend in rt.NATIVE_COLUMNAR_COUNT_SUM_BACKENDS:
            with self.subTest(backend=backend):
                plan = rt.plan_columnar_aggregate_lowering(backend)
                self.assertEqual(plan.transfer_path, "direct_columnar_record_set_to_columnar_payload")
                self.assertFalse(plan.uses_compatibility_wrapper)
                self.assertFalse(plan.materializes_input_rows_for_wrapper)
                self.assertTrue(plan.direct_columnar_record_set_api)
                self.assertFalse(plan.true_zero_copy_authorized)

    def test_app_native_path_uses_direct_preparation_without_row_mapping(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("rt.prepare_embree_columnar_record_set", source)
        self.assertIn("rt.prepare_optix_columnar_record_set", source)
        self.assertNotIn("columnar_record_set_to_row_mappings(fixture)", source)

    def test_direct_embree_preparation_matches_cpu_when_available(self) -> None:
        _require_embree()
        query = rt.columnar_plan_to_grouped_query(app.make_plan("sum"))
        dataset = rt.prepare_embree_columnar_record_set(
            app.make_fixture(),
            primary_fields=("ship_year", "discount", "quantity"),
        )
        try:
            self.assertEqual(dataset.grouped_sum(query), tuple(app.run_result_mode("sum")["rows"]))
        finally:
            dataset.close()

    def test_direct_optix_preparation_matches_cpu_when_available(self) -> None:
        _require_optix()
        query = rt.columnar_plan_to_grouped_query(app.make_plan("count"))
        dataset = rt.prepare_optix_columnar_record_set(
            app.make_fixture(),
            primary_fields=("ship_year", "discount", "quantity"),
        )
        try:
            self.assertEqual(dataset.grouped_count(query), tuple(app.run_result_mode("count")["rows"]))
        finally:
            dataset.close()

    def test_report_records_boundary_and_next_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("direct ColumnarRecordSet preparation", text)
        self.assertIn("does not add native ABI", text)
        self.assertIn("does not authorize true zero-copy", text)
        self.assertIn("typed host buffer or partner-resident column handoff", text)
        self.assertIn("18 tests OK, 1 skipped", text)

    def test_pod_optix_artifacts_record_direct_path_parity(self) -> None:
        app_payload = json.loads(POD_APP.read_text(encoding="utf-8"))
        matrix = json.loads(POD_MATRIX.read_text(encoding="utf-8"))
        self.assertTrue(app_payload["all_match_cpu_reference"])
        self.assertTrue(matrix["cases"]["optix"]["all_match_cpu_reference"])
        lowering = app_payload["modes"]["count"]["metadata"]["lowering_plan"]
        self.assertEqual(lowering["transfer_path"], "direct_columnar_record_set_to_columnar_payload")
        self.assertFalse(lowering["materializes_input_rows_for_wrapper"])
        self.assertTrue(lowering["direct_columnar_record_set_api"])
        self.assertFalse(lowering["true_zero_copy_authorized"])


if __name__ == "__main__":
    unittest.main()
