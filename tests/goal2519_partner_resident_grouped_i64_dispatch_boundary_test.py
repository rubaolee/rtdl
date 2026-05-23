from inspect import signature
import json
from pathlib import Path
import unittest

import rtdsl as rt

from tests.goal2505_partner_resident_columnar_descriptor_contract_test import FakeCudaColumn
from tests.goal2505_partner_resident_columnar_descriptor_contract_test import _record_set


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2519_partner_resident_grouped_i64_dispatch_boundary_2026-05-23.md"
POD_SCRIPT = ROOT / "scripts/goal2519_partner_resident_grouped_i64_dispatch_boundary_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2519_partner_resident_grouped_i64_dispatch_boundary_pod_2026-05-23.json"
RAYDB_APP = ROOT / "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"


class Goal2519PartnerResidentGroupedI64DispatchBoundaryTest(unittest.TestCase):
    def test_dispatcher_is_exported_with_supported_reductions(self) -> None:
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTIONS,
            ("count", "sum", "min", "max", "sum_count", "stats"),
        )
        self.assertIn("OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTIONS", rt.__all__)
        self.assertIn("run_optix_partner_resident_columnar_grouped_i64_reduction", rt.__all__)
        self.assertIn("run_optix_partner_resident_columnar_grouped_stats_i64", rt.__all__)
        parameters = signature(rt.run_optix_partner_resident_columnar_grouped_i64_reduction).parameters
        for name in ("reduction", "allow_experimental_native", "group_capacity", "semantic_aggregate"):
            self.assertIn(name, parameters)

    def test_dispatcher_fails_closed_before_native_symbol_lookup(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(
            _record_set(columns={"revenue": FakeCudaColumn(ptr=0x3000, dtype="int64")}),
            backend="optix",
        )
        query = {"predicates": (), "group_keys": ("region_id",), "value_field": "revenue"}
        with self.assertRaisesRegex(RuntimeError, "allow_experimental_native=True"):
            rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
                descriptor,
                query,
                reduction="sum",
            )
        with self.assertRaisesRegex(ValueError, "unsupported partner-resident grouped i64 reduction"):
            rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
                descriptor,
                query,
                reduction="avg",
                allow_experimental_native=True,
                group_capacity=3,
            )
        with self.assertRaisesRegex(ValueError, "explicit group_capacity"):
            rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
                descriptor,
                query,
                reduction="sum",
                allow_experimental_native=True,
            )
        with self.assertRaisesRegex(ValueError, "requires a value_field"):
            rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
                descriptor,
                {"predicates": (), "group_keys": ("region_id",)},
                reduction="sum_count",
                allow_experimental_native=True,
                group_capacity=3,
            )

    def test_runtime_metadata_contract_is_app_agnostic(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("_partner_resident_grouped_i64_reduction_metadata", source)
        self.assertIn('"semantic_aggregate"', source)
        self.assertIn('"public_speedup_claim_authorized"', source)
        self.assertIn('"true_zero_copy_authorized"', source)
        self.assertNotIn("raydb_style_columnar_aggregate", source)
        self.assertNotIn("avg_as_sum_count", source)

    def test_raydb_app_uses_dispatcher_not_low_level_symbols(self) -> None:
        source = RAYDB_APP.read_text(encoding="utf-8")
        self.assertIn("run_optix_partner_resident_columnar_grouped_i64_reduction", source)
        for low_level_name in (
            "run_optix_partner_resident_columnar_grouped_count_i64(",
            "run_optix_partner_resident_columnar_grouped_sum_i64(",
            "run_optix_partner_resident_columnar_grouped_min_i64(",
            "run_optix_partner_resident_columnar_grouped_max_i64(",
            "run_optix_partner_resident_columnar_grouped_sum_count_i64(",
            "run_optix_partner_resident_columnar_grouped_stats_i64(",
        ):
            self.assertNotIn(low_level_name, source)
        self.assertIn("semantic_aggregate=mode", source)
        self.assertIn('reduction = "sum_count"', source)
        self.assertIn("composite_lowering", source)

    def test_report_and_runner_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        runner = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("Goal2519", report)
        self.assertIn("run_optix_partner_resident_columnar_grouped_i64_reduction", report)
        self.assertIn("fail-closed", report)
        self.assertIn("No", report)
        self.assertIn("true zero-copy", report)
        self.assertIn("public", report)
        self.assertIn("direct_dispatch_all_match_cpu_reference", runner)
        self.assertIn("app_direct_low_level_symbols_absent", runner)

    def test_pod_artifact_records_dispatcher_cuda_parity(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertIs(payload["cuda_available"], True)
        self.assertEqual(payload["dispatcher_reductions"], ["count", "sum", "min", "max", "sum_count"])
        self.assertIn("stats", rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTIONS)
        self.assertIs(payload["app_uses_dispatcher"], True)
        self.assertIs(payload["app_direct_low_level_symbols_absent"], True)
        self.assertIs(payload["native_avg_symbol_absent"], True)
        self.assertIs(payload["direct_dispatch_all_match_cpu_reference"], True)
        self.assertIs(payload["app_suite_all_match_cpu_reference"], True)
        self.assertEqual(payload["app_suite_modes"], ["count", "sum", "min", "max", "avg_as_sum_count"])
        avg_metadata = payload["avg_metadata"]
        self.assertIs(avg_metadata["partner_resident_grouped_i64_dispatcher"], True)
        self.assertEqual(avg_metadata["semantic_aggregate"], "avg_as_sum_count")
        self.assertEqual(avg_metadata["reduction"], "sum_count")
        self.assertEqual(avg_metadata["native_launch_count"], 1)
        self.assertIs(avg_metadata["fused_native_reduction"], True)
        self.assertIs(avg_metadata["generic_sum_count_abi_used"], True)
        self.assertIs(avg_metadata["native_avg_abi_added"], False)
        self.assertIs(avg_metadata["public_speedup_claim_authorized"], False)
        self.assertIs(avg_metadata["true_zero_copy_authorized"], False)


if __name__ == "__main__":
    unittest.main()
