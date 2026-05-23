from inspect import signature
import json
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app

from tests.goal2505_partner_resident_columnar_descriptor_contract_test import FakeCudaColumn
from tests.goal2505_partner_resident_columnar_descriptor_contract_test import _record_set


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2517_partner_resident_fused_sum_count_i64_2026-05-23.md"
POD_SCRIPT = ROOT / "scripts/goal2517_partner_resident_fused_sum_count_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2517_partner_resident_fused_sum_count_pod_2026-05-23.json"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
RAYDB_APP = ROOT / "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py"


class Goal2517PartnerResidentFusedSumCountI64Test(unittest.TestCase):
    def test_sum_count_symbol_and_entrypoint_are_exported(self) -> None:
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL,
            "rtdl_optix_columnar_device_payload_grouped_sum_count_i64_with_capacity",
        )
        self.assertIn("OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL", rt.__all__)
        self.assertIn("run_optix_partner_resident_columnar_grouped_sum_count_i64", rt.__all__)
        self.assertIn(
            "group_capacity",
            signature(rt.run_optix_partner_resident_columnar_grouped_sum_count_i64).parameters,
        )

    def test_python_entrypoint_fails_closed_before_native_load_when_invalid(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(
            _record_set(columns={"revenue": FakeCudaColumn(ptr=0x3000, dtype="int64")}),
            backend="optix",
        )
        query = {"predicates": (), "group_keys": ("region_id",), "value_field": "revenue"}
        with self.assertRaisesRegex(RuntimeError, "allow_experimental_native=True"):
            rt.run_optix_partner_resident_columnar_grouped_sum_count_i64(descriptor, query)
        with self.assertRaisesRegex(ValueError, "explicit group_capacity"):
            rt.run_optix_partner_resident_columnar_grouped_sum_count_i64(
                descriptor,
                query,
                allow_experimental_native=True,
            )
        with self.assertRaisesRegex(ValueError, "requires a value_field"):
            rt.run_optix_partner_resident_columnar_grouped_sum_count_i64(
                descriptor,
                {"predicates": (), "group_keys": ("region_id",)},
                allow_experimental_native=True,
                group_capacity=3,
            )

    def test_native_sources_define_generic_fused_sum_count_reduction(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        symbol = "rtdl_optix_columnar_device_payload_grouped_sum_count_i64_with_capacity"
        for source in (api, prelude, runtime):
            self.assertIn(symbol, source)
        self.assertIn("struct RtdlDbGroupedSumCountRow", prelude)
        self.assertIn("RTDL_GROUPED_OP_SUM_COUNT = 5u", workloads)
        self.assertIn("device_column_grouped_i64_compact_sum_count_kernel", workloads)
        self.assertIn("compact_sum_count_fn", workloads)
        self.assertIn("download(sum_count_rows.data(), d_rows.ptr, compact_row_count)", workloads)

    def test_app_avg_mode_uses_fused_generic_sum_count_without_native_average_abi(self) -> None:
        source = RAYDB_APP.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("run_optix_partner_resident_columnar_grouped_i64_reduction", source)
        self.assertIn("dispatch_metadata", source)
        self.assertIn("fused_native_reduction", runtime)
        self.assertIn("generic_sum_count_abi_used", runtime)
        self.assertIn('reduction = "sum_count"', source)
        self.assertNotIn("run_optix_partner_resident_columnar_grouped_sum_count_i64(", source)
        self.assertNotIn("run_optix_partner_resident_columnar_grouped_avg", source)

    def test_report_and_runner_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        runner = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("Goal2517", report)
        self.assertIn("generic fused sum_count", report)
        self.assertIn("no native average ABI", report)
        self.assertIn("true zero-copy", report)
        self.assertIn("public speedup", report)
        self.assertIn("direct_sum_count_matches_cpu", runner)
        self.assertIn("native_sum_count_symbol_present", runner)

    def test_pod_artifact_records_fused_cuda_parity(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertIs(payload["cuda_available"], True)
        self.assertIs(payload["direct_sum_count_matches_cpu"], True)
        self.assertIs(payload["avg_matches_cpu"], True)
        self.assertIs(payload["app_suite_all_match_cpu_reference"], True)
        self.assertEqual(payload["app_suite_modes"], ["count", "sum", "min", "max", "avg_as_sum_count"])
        self.assertEqual(payload["avg_metadata"]["composite_lowering"], ["sum", "count"])
        self.assertEqual(payload["avg_metadata"]["native_launch_count"], 1)
        self.assertIs(payload["avg_metadata"]["fused_native_reduction"], True)
        self.assertIs(payload["avg_metadata"]["generic_sum_count_abi_used"], True)
        self.assertIs(payload["avg_metadata"]["native_avg_abi_added"], False)
        self.assertIs(payload["native_avg_symbol_absent"], True)
        self.assertIs(payload["native_sum_count_symbol_present"], True)
        self.assertIn("No public speedup", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
