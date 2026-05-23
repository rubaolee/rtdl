from inspect import signature
import json
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app

from tests.goal2505_partner_resident_columnar_descriptor_contract_test import _record_set


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2513_partner_resident_group_capacity_contract_2026-05-22.md"
POD_SCRIPT = ROOT / "scripts/goal2513_partner_resident_group_capacity_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2513_partner_resident_group_capacity_pod_2026-05-22.json"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"


class Goal2513PartnerResidentGroupCapacityContractTest(unittest.TestCase):
    def test_capacity_symbols_and_python_keywords_are_exported(self) -> None:
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL,
            "rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity",
        )
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_WITH_CAPACITY_SYMBOL,
            "rtdl_optix_columnar_device_payload_grouped_sum_i64_with_capacity",
        )
        self.assertIn(
            "group_capacity",
            signature(rt.run_optix_partner_resident_columnar_grouped_count_i64).parameters,
        )
        self.assertIn(
            "group_capacity",
            signature(rt.run_optix_partner_resident_columnar_grouped_sum_i64).parameters,
        )

    def test_sources_use_runtime_capacity_not_kernel_literal_limit(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity", api)
        self.assertIn("rtdl_optix_columnar_device_payload_grouped_sum_i64_with_capacity", api)
        self.assertIn("params.group_capacity", workloads)
        self.assertIn("group_capacity must be in 1..1000000", workloads)
        self.assertIn("dense non-negative group keys below group_capacity", workloads)
        self.assertNotIn("RTDL_MAX_GROUPS = 65536u", workloads)
        self.assertIn("OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL", runtime)

    def test_python_capacity_validation_fails_before_native_load(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        query = {"predicates": (), "group_keys": ("region_id",), "value_field": "region_id"}
        for invalid in (0, -1, True, "3", 1_000_001):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "group_capacity"):
                    rt.run_optix_partner_resident_columnar_grouped_count_i64(
                        descriptor,
                        query,
                        allow_experimental_native=True,
                        group_capacity=invalid,
                    )

    def test_app_infers_dense_capacity_and_docs_record_boundary(self) -> None:
        self.assertEqual(app._infer_dense_group_capacity(app.make_fixture(), app.make_plan("count")), 3)
        report = REPORT.read_text(encoding="utf-8")
        script = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("group_capacity=3", report)
        self.assertIn("group_capacity=2", report)
        self.assertIn("true zero-copy claim", report)
        self.assertIn("group_capacity", script)
        self.assertIn("expected_capacity_error", script)

    def test_pod_artifact_records_compact_capacity_and_fail_closed_probe(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["group_capacity"], 3)
        self.assertEqual(payload["legacy_default_capacity"], 65536)
        self.assertIs(payload["capacity_is_explicit"], True)
        self.assertIs(payload["count_matches_cpu"], True)
        self.assertIs(payload["sum_matches_cpu"], True)
        self.assertIs(payload["capacity_error_matched"], True)
        self.assertIn("below group_capacity", payload["expected_capacity_error"])
        self.assertEqual(payload["app_suite_group_capacity"], 3)
        self.assertIs(payload["app_suite_all_match_cpu_reference"], True)


if __name__ == "__main__":
    unittest.main()
