from inspect import signature
import json
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app

from tests.goal2505_partner_resident_columnar_descriptor_contract_test import FakeCudaColumn
from tests.goal2505_partner_resident_columnar_descriptor_contract_test import _record_set


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2515_partner_resident_grouped_min_max_i64_2026-05-22.md"
POD_SCRIPT = ROOT / "scripts/goal2515_partner_resident_grouped_min_max_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2515_partner_resident_grouped_min_max_pod_2026-05-22.json"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
LOWERING = ROOT / "src/rtdsl/columnar_aggregate_reference.py"


class Goal2515PartnerResidentGroupedMinMaxI64Test(unittest.TestCase):
    def test_min_max_symbols_and_entrypoints_are_exported(self) -> None:
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MIN_I64_WITH_CAPACITY_SYMBOL,
            "rtdl_optix_columnar_device_payload_grouped_min_i64_with_capacity",
        )
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MAX_I64_WITH_CAPACITY_SYMBOL,
            "rtdl_optix_columnar_device_payload_grouped_max_i64_with_capacity",
        )
        self.assertIn("run_optix_partner_resident_columnar_grouped_min_i64", rt.__all__)
        self.assertIn("run_optix_partner_resident_columnar_grouped_max_i64", rt.__all__)
        self.assertIn(
            "group_capacity",
            signature(rt.run_optix_partner_resident_columnar_grouped_min_i64).parameters,
        )
        self.assertIn(
            "group_capacity",
            signature(rt.run_optix_partner_resident_columnar_grouped_max_i64).parameters,
        )

    def test_python_entrypoints_fail_closed_before_native_load_when_invalid(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(
            _record_set(columns={"revenue": FakeCudaColumn(ptr=0x3000, dtype="int64")}),
            backend="optix",
        )
        query = {"predicates": (), "group_keys": ("region_id",), "value_field": "revenue"}
        with self.assertRaisesRegex(RuntimeError, "allow_experimental_native=True"):
            rt.run_optix_partner_resident_columnar_grouped_min_i64(descriptor, query)
        with self.assertRaisesRegex(RuntimeError, "allow_experimental_native=True"):
            rt.run_optix_partner_resident_columnar_grouped_max_i64(descriptor, query)
        with self.assertRaisesRegex(ValueError, "explicit group_capacity"):
            rt.run_optix_partner_resident_columnar_grouped_min_i64(
                descriptor,
                query,
                allow_experimental_native=True,
            )
        with self.assertRaisesRegex(ValueError, "group_capacity"):
            rt.run_optix_partner_resident_columnar_grouped_max_i64(
                descriptor,
                query,
                allow_experimental_native=True,
                group_capacity=0,
            )

    def test_native_sources_define_generic_signed_min_max_reductions(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_optix_columnar_device_payload_grouped_min_i64_with_capacity",
            "rtdl_optix_columnar_device_payload_grouped_max_i64_with_capacity",
        ):
            self.assertIn(symbol, api)
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, runtime)
        self.assertIn("RTDL_GROUPED_OP_MIN = 3u", workloads)
        self.assertIn("RTDL_GROUPED_OP_MAX = 4u", workloads)
        self.assertIn("device_atomic_min_i64", workloads)
        self.assertIn("device_atomic_max_i64", workloads)
        self.assertIn("atomicCAS", workloads)
        self.assertIn("device_column_grouped_i64_init_values_kernel", workloads)
        self.assertIn("download(sum_rows.data(), d_rows.ptr, compact_row_count)", workloads)

    def test_lowering_and_app_modes_include_min_max_without_public_claims(self) -> None:
        plan = rt.plan_columnar_aggregate_lowering(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
        for aggregate in ("count", "sum", "min", "max"):
            self.assertIn(aggregate, plan.supported_aggregates)
        self.assertEqual(app.OPTIX_PARTNER_RESIDENT_RESULT_MODES[:4], ("count", "sum", "min", "max"))
        self.assertNotIn("raydb", LOWERING.read_text(encoding="utf-8").lower())
        self.assertIn("true zero-copy", plan.claim_boundary)
        self.assertIn("public speedup", plan.claim_boundary)

    def test_report_and_pod_runner_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        runner = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("Goal2515", report)
        self.assertIn("count/sum/min/max", report)
        self.assertIn("signed int64", report)
        self.assertIn("true zero-copy", report)
        self.assertIn("public speedup", report)
        self.assertIn("run_optix_partner_resident_columnar_grouped_min_i64", runner)
        self.assertIn("run_optix_partner_resident_columnar_grouped_max_i64", runner)
        self.assertIn("signed_min_matches_expected", runner)
        self.assertIn("app_suite_modes", runner)

    def test_pod_artifact_records_min_max_cuda_parity(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertIs(payload["cuda_available"], True)
        self.assertIs(payload["app_suite_all_match_cpu_reference"], True)
        self.assertEqual(payload["app_suite_modes"], ["count", "sum", "min", "max"])
        self.assertIs(payload["min_matches_cpu"], True)
        self.assertIs(payload["max_matches_cpu"], True)
        self.assertIs(payload["signed_min_matches_expected"], True)
        self.assertIs(payload["signed_max_matches_expected"], True)
        self.assertEqual(payload["signed_min_rows"][0], {"min": -5, "region_id": 0})
        self.assertEqual(payload["signed_max_rows"][1], {"max": 7, "region_id": 1})
        self.assertIn("No public speedup", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
