from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4591_v3_0_m192_c_abi_host_external_runtime_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4591_v3_0_m192_c_abi_host_external_runtime_gate_2026-06-17.md"
EXAMPLE = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/c_api_host_runtime_client.c"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4591V30M192CAbiHostExternalRuntimeGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4591_m192_v3_c_abi_host_external_runtime_gate")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_host_external_runtime_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_host_external_runtime.goal4591.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_runtime_validates_success_and_rejections(self) -> None:
        self.assertTrue(self.checked_in["checks"]["shared_library_build_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_compile_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_run_ok"])
        self.assertTrue(self.checked_in["checks"]["runtime_validated_all_cases"])
        for name, passed in self.checked_in["validated_cases"].items():
            self.assertTrue(passed, name)
        stdout = self.checked_in["client_result"]["client_run"]["stdout"]
        self.assertIn("validated_host_external_runtime_cases=3", stdout)

    def test_report_index_example_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4591 / V3 M192", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4591 C ABI host external runtime gate", INDEX.read_text(encoding="utf-8"))
        example = EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("host_external_runtime_metadata_ok", example)
        self.assertEqual("validated", self.checked_in["support_matrix"]["host_external_runtime_metadata"])
        self.assertEqual("rejected_unsupported", self.checked_in["support_matrix"]["cuda_external_runtime"])
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
