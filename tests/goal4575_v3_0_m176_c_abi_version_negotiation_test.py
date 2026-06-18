from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4575_v3_0_m176_c_abi_version_negotiation_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4575_v3_0_m176_c_abi_version_negotiation_2026-06-17.md"
MANIFEST = ROOT / "docs/learn/v3_0_c_abi_symbol_manifest_v0_1_3.json"
M176_MANIFEST = ROOT / "docs/learn/v3_0_c_abi_symbol_manifest_v0_1_2.json"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4575V30M176CAbiVersionNegotiationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4575_m176_v3_c_abi_version_negotiation")
        cls.packet = cls.module.build_packet(ROOT, run_runtime=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_version_negotiation_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_version_negotiation.goal4575.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_runtime_smoke_proves_fail_closed_compatibility(self) -> None:
        runtime = self.checked_in["runtime_build"]
        self.assertTrue(runtime["ok"])
        smoke = runtime["ctypes_smoke"]["checks"]
        self.assertTrue(smoke["current_abi_is_compatible"])
        self.assertTrue(smoke["previous_patch_is_compatible"])
        self.assertTrue(smoke["future_patch_is_not_compatible"])
        self.assertTrue(smoke["future_minor_context_rejected"])

    def test_manifest_report_index_and_boundaries_are_wired(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        m176_manifest = json.loads(M176_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual("0.1.3", manifest["abi_version"])
        self.assertEqual("0.1.2", m176_manifest["abi_version"])
        self.assertIn("rtdl_abi_is_compatible", manifest["symbols"])
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4575 / V3 M176", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4575 C ABI version negotiation", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
