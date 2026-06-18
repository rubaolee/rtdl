from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4574_v3_0_m175_c_abi_patch_version_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4574_v3_0_m175_c_abi_patch_version_refresh_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
CURRENT_MANIFEST = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_3.json"
M175_MANIFEST = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_1.json"


class Goal4574V30M175CAbiPatchVersionRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4574_m175_v3_c_abi_patch_version_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_patch_version_refresh_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_patch_version_refresh.goal4574.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_m175_manifest_is_retained_and_current_manifest_advanced(self) -> None:
        manifest = json.loads(CURRENT_MANIFEST.read_text(encoding="utf-8"))
        m175_manifest = json.loads(M175_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual("0.1.3", manifest["abi_version"])
        self.assertFalse(manifest["stable"])
        self.assertEqual("0.1.1", m175_manifest["abi_version"])
        self.assertFalse(m175_manifest["stable"])
        self.assertIn("rtdl_context_set_external_runtime", manifest["symbols"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4574 / V3 M175", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4574 C ABI patch version refresh", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
