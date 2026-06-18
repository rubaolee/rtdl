from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4568_v3_0_m169_zero_copy_interop_contract_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4568_v3_0_m169_zero_copy_interop_contract_2026-06-17.md"
DOC = ROOT / "docs/learn/v3_0_zero_copy_interop_contract.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4568V30M169ZeroCopyInteropContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4568_m169_v3_zero_copy_interop_contract")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_zero_copy_interop_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.zero_copy_interop_contract.goal4568.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_descriptor_states_keep_claims_separated(self) -> None:
        borrowed = self.packet["borrowed_descriptor"]
        measured = self.packet["measured_descriptor"]
        self.assertEqual("borrowed_device_pointer_unmeasured", borrowed["transfer_status"])
        self.assertFalse(borrowed["zero_copy_claim_authorized"])
        self.assertTrue(measured["zero_copy_claim_authorized"])
        self.assertFalse(measured["public_speedup_claim_authorized"])

    def test_report_docs_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4568 / V3 M169", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4568 zero-copy interop contract", INDEX.read_text(encoding="utf-8"))
        doc = DOC.read_text(encoding="utf-8")
        self.assertIn("not an implemented C ABI device-buffer", doc)
        self.assertIn("route and not public true-zero-copy wording", doc)
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
