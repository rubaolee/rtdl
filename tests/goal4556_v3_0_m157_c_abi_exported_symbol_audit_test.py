from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4556V30M157CAbiExportedSymbolAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4556_m157_v3_c_abi_exported_symbol_audit")
        cls.packet = cls.module.build_packet(ROOT, run_audit=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_symbol_contract_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_exported_symbol_audit.goal4556.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_pod_symbol_audit_passed(self) -> None:
        audit = self.checked_in["audit"]
        self.assertTrue(audit["ok"])
        self.assertEqual([], audit["missing_symbols"])
        self.assertTrue(self.checked_in["checks"]["all_expected_symbols_exported"])
        self.assertGreaterEqual(len(audit["exported_symbols"]), len(self.checked_in["expected_symbols"]))

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4556 / V3 M157", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4556 C ABI exported symbol audit", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
