from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4566_v3_0_m167_c_abi_symbol_manifest_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4566_v3_0_m167_c_abi_symbol_manifest_2026-06-17.md"
MANIFEST = ROOT / "docs/learn/v3_0_c_abi_symbol_manifest_v0_1_0.json"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4566V30M167CAbiSymbolManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4566_m167_v3_c_abi_symbol_manifest")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_symbol_manifest_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_symbol_manifest.goal4566.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_manifest_is_draft_and_lists_current_symbols(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertFalse(manifest["stable"])
        self.assertEqual("0.1.0", manifest["abi_version"])
        self.assertEqual(15, len(manifest["symbols"]))
        self.assertIn("rtdl_index_build", manifest["symbols"])
        self.assertIn("rtdl_query_execute", manifest["symbols"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4566 / V3 M167", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4566 C ABI symbol manifest", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
