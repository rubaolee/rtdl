import json
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2516_partner_resident_composite_avg_sum_count_2026-05-22.md"
POD_SCRIPT = ROOT / "scripts/goal2516_partner_resident_composite_avg_sum_count_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2516_partner_resident_composite_avg_sum_count_pod_2026-05-22.json"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
LOWERING = ROOT / "src/rtdsl/columnar_aggregate_reference.py"


class Goal2516PartnerResidentCompositeAvgSumCountTest(unittest.TestCase):
    def test_composite_lowering_contract_is_generic_and_exported(self) -> None:
        self.assertEqual(rt.COMPOSITE_COLUMNAR_AGGREGATE_LOWERINGS, {"avg_as_sum_count": ("sum", "count")})
        plan = app.make_plan("avg_as_sum_count")
        decomposed = rt.decompose_columnar_aggregate_plan(plan)
        self.assertEqual(tuple(item.aggregate for item in decomposed), ("sum", "count"))
        self.assertEqual(decomposed[0].value_field, "revenue")
        self.assertIsNone(decomposed[1].value_field)
        self.assertIn("decompose_columnar_aggregate_plan", rt.__all__)
        self.assertIn("merge_columnar_grouped_sum_count_rows", rt.__all__)

    def test_merge_matches_cpu_reference_rows_without_native_execution(self) -> None:
        fixture = app.make_fixture()
        plan = app.make_plan("avg_as_sum_count")
        sum_rows = rt.evaluate_columnar_grouped_aggregate(fixture, {**plan, "aggregate": "sum"}).rows
        count_rows = rt.evaluate_columnar_grouped_aggregate(
            fixture,
            {
                "predicates": plan["predicates"],
                "group_keys": plan["group_keys"],
                "aggregate": "count",
            },
        ).rows
        merged = rt.merge_columnar_grouped_sum_count_rows(
            tuple(reversed(sum_rows)),
            tuple(reversed(count_rows)),
            group_keys=plan["group_keys"],
        )
        expected = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
        self.assertEqual(merged, expected)

    def test_partner_lowering_and_app_support_composite_avg(self) -> None:
        lowering = rt.plan_columnar_aggregate_lowering(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
        self.assertEqual(lowering.supported_aggregates, rt.SUPPORTED_AGGREGATES)
        self.assertEqual(lowering.unsupported_aggregates, ())
        self.assertIn("composite avg_as_sum_count", lowering.claim_boundary)
        self.assertEqual(
            app.OPTIX_PARTNER_RESIDENT_RESULT_MODES,
            ("count", "sum", "min", "max", "avg_as_sum_count"),
        )

    def test_no_native_avg_symbol_or_app_vocabulary_in_generic_lowering(self) -> None:
        native_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (OPTIX_API, OPTIX_PRELUDE, OPTIX_WORKLOADS)
        ).lower()
        self.assertNotIn("rtdl_optix_columnar_device_payload_grouped_avg", native_text)
        self.assertNotIn("run_device_column_grouped_avg", native_text)
        lowering_source = LOWERING.read_text(encoding="utf-8").lower()
        for forbidden in ("raydb", "sql", "database", "ssb"):
            self.assertNotIn(forbidden, lowering_source)

    def test_report_and_runner_record_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        runner = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("Goal2516", report)
        self.assertIn("avg_as_sum_count = sum + count", report)
        self.assertIn("no native average ABI", report)
        self.assertIn("true zero-copy", report)
        self.assertIn("public speedup", report)
        self.assertIn("native_avg_symbol_absent", runner)
        self.assertIn("avg_matches_cpu", runner)

    def test_pod_artifact_records_composite_cuda_parity(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertIs(payload["cuda_available"], True)
        self.assertIs(payload["avg_matches_cpu"], True)
        self.assertIs(payload["app_suite_all_match_cpu_reference"], True)
        self.assertEqual(payload["app_suite_modes"], ["count", "sum", "min", "max", "avg_as_sum_count"])
        self.assertEqual(payload["avg_metadata"]["composite_lowering"], ["sum", "count"])
        self.assertEqual(payload["avg_metadata"]["native_launch_count"], 2)
        self.assertIs(payload["avg_metadata"]["native_avg_abi_added"], False)
        self.assertIs(payload["native_avg_symbol_absent"], True)
        self.assertIn("No public speedup", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
