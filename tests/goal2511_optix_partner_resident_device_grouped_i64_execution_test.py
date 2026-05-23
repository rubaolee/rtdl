import json
from pathlib import Path
import unittest

import rtdsl as rt

from tests.goal2505_partner_resident_columnar_descriptor_contract_test import _record_set


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2511_optix_partner_resident_device_grouped_i64_execution_2026-05-22.md"
POD_ARTIFACT = ROOT / "docs/reports/goal2511_optix_partner_resident_device_grouped_i64_pod_2026-05-22.json"
POD_SCRIPT = ROOT / "scripts/goal2511_optix_partner_resident_device_grouped_i64_pod.py"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"


class Goal2511OptixPartnerResidentDeviceGroupedI64ExecutionTest(unittest.TestCase):
    def test_experimental_symbols_are_exported(self) -> None:
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_SYMBOL,
            "rtdl_optix_columnar_device_payload_grouped_count_i64",
        )
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_SYMBOL,
            "rtdl_optix_columnar_device_payload_grouped_sum_i64",
        )
        self.assertIn("run_optix_partner_resident_columnar_grouped_count_i64", rt.__all__)
        self.assertIn("run_optix_partner_resident_columnar_grouped_sum_i64", rt.__all__)

    def test_python_entrypoints_fail_closed_without_experimental_flag(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        query = {"predicates": (), "group_keys": ("region_id",), "value_field": "region_id"}
        with self.assertRaisesRegex(RuntimeError, "allow_experimental_native=True"):
            rt.run_optix_partner_resident_columnar_grouped_count_i64(descriptor, query)
        with self.assertRaisesRegex(RuntimeError, "allow_experimental_native=True"):
            rt.run_optix_partner_resident_columnar_grouped_sum_i64(descriptor, query)

    def test_native_sources_define_device_side_grouped_i64_execution(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_optix_columnar_device_payload_grouped_count_i64",
            "rtdl_optix_columnar_device_payload_grouped_sum_i64",
        ):
            self.assertIn(symbol, api)
            self.assertIn(symbol, runtime)
        self.assertIn("device_column_grouped_i64_kernel", workloads)
        self.assertIn("atomicAdd(params.group_counts + group", workloads)
        self.assertIn("atomicAdd(params.group_sums + group", workloads)
        self.assertIn("params.group_capacity", workloads)
        self.assertIn("dense non-negative group keys below group_capacity", workloads)

    def test_pod_runner_checks_real_cuda_parity_when_available(self) -> None:
        text = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("torch.tensor", text)
        self.assertIn("allow_experimental_native=True", text)
        self.assertIn("run_optix_partner_resident_columnar_grouped_count_i64", text)
        self.assertIn("run_optix_partner_resident_columnar_grouped_sum_i64", text)
        self.assertIn("count_matches_cpu", text)
        self.assertIn("sum_matches_cpu", text)

    def test_report_records_experimental_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2511", text)
        self.assertIn("experimental-only", text)
        self.assertIn("device-side predicate evaluation", text)
        self.assertIn("device-side grouped count/sum reduction", text)
        self.assertIn("dense", text)
        self.assertIn("non-negative group keys below the configured group capacity", text)
        self.assertIn("No speedup or zero-copy claim", text)
        self.assertIn("count_matches_cpu: true", text)
        self.assertIn("sum_matches_cpu: true", text)

    def test_pod_artifact_records_cuda_count_and_sum_parity(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertIs(payload["cuda_available"], True)
        self.assertIs(payload["count_matches_cpu"], True)
        self.assertIs(payload["sum_matches_cpu"], True)
        self.assertEqual(
            payload["count_rows"],
            [
                {"count": 2, "region_id": 0},
                {"count": 1, "region_id": 1},
                {"count": 1, "region_id": 2},
            ],
        )
        self.assertEqual(
            payload["sum_rows"],
            [
                {"region_id": 0, "sum": 190},
                {"region_id": 1, "sum": 200},
                {"region_id": 2, "sum": 80},
            ],
        )
        self.assertEqual(payload["descriptor"]["device"], "cuda:0")
        self.assertIn("torch", payload["descriptor"]["source_protocols"])
        self.assertIn("No public speedup", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
