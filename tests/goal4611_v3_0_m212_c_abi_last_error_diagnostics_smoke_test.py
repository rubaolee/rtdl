from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4611_v3_0_m212_c_abi_last_error_diagnostics_smoke_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4611_v3_0_m212_c_abi_last_error_diagnostics_smoke_2026-06-17.md"
OWNERSHIP_DOC = ROOT / "docs/learn/v3_0_c_abi_ownership_threading_contract.md"
ARCHITECTURE_DOC = ROOT / "docs/learn/v3_0_embeddability_architecture_strategy.md"
BINDING_MATRIX = ROOT / "docs/learn/v3_0_binding_and_device_interop_matrix.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4611V30M212CAbiLastErrorDiagnosticsSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4611_m212_v3_c_abi_last_error_diagnostics_smoke")
        cls.packet = cls.module.build_packet(ROOT, run_client=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_last_error_diagnostics_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_last_error_diagnostics.goal4611.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_last_error_smoke_passed(self) -> None:
        client = self.checked_in["client_result"]
        self.assertTrue(client["ok"])
        self.assertTrue(client["shared_library"]["ok"])
        self.assertTrue(client["client_compile"]["ok"])
        self.assertTrue(client["client_run"]["ok"])
        self.assertTrue(self.checked_in["checks"]["runtime_validated_all_lifecycle_cases"])
        for name, passed in self.checked_in["validated_cases"].items():
            self.assertTrue(passed, name)
        self.assertIn("validated_last_error_lifecycle_cases=11", client["client_run"]["stdout"])

    def test_docs_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4611 / V3 M212", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4611 C ABI last-error diagnostics smoke", INDEX.read_text(encoding="utf-8"))
        self.assertIn("Successful C ABI calls that mutate a context clear", OWNERSHIP_DOC.read_text(encoding="utf-8"))
        self.assertIn("As of Goal4611", ARCHITECTURE_DOC.read_text(encoding="utf-8"))
        self.assertIn("C ABI status/last-error diagnostics", BINDING_MATRIX.read_text(encoding="utf-8"))
        matrix = self.checked_in["support_matrix"]
        self.assertEqual("validated_source_tree_smoke", matrix["status_string_diagnostics"])
        self.assertEqual("blocked_use_status_codes", matrix["last_error_text_as_machine_contract"])
        self.assertTrue(self.checked_in["claim_boundary"]["diagnostic_lifecycle_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "diagnostic_lifecycle_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
