from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4551_v3_0_m152_c_abi_header_compile_smoke_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4551_v3_0_m152_c_abi_header_compile_smoke_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4551V30M152CAbiHeaderCompileSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4551_m152_v3_c_abi_header_compile_smoke")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_header_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_header_compile_smoke.goal4551.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_compile_smoke_passed(self) -> None:
        compile_results = self.checked_in["compile_results"]
        self.assertTrue(compile_results["c"]["ok"])
        self.assertTrue(compile_results["cxx"]["ok"])
        self.assertTrue(self.checked_in["checks"]["c_header_compile_ok"])
        self.assertTrue(self.checked_in["checks"]["cxx_header_compile_ok"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4551 / V3 M152", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4551 C ABI header compile smoke", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
