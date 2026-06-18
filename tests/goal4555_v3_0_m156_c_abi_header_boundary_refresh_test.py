from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "include/rtdl/rtdl.h"
PACKET = ROOT / "docs/reports/goal4555_v3_0_m156_c_abi_header_boundary_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4555_v3_0_m156_c_abi_header_boundary_refresh_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4555V30M156CAbiHeaderBoundaryRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4555_m156_v3_c_abi_header_boundary_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_header_boundary_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_header_boundary_refresh.goal4555.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_header_wording_is_current(self) -> None:
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("minimal lifecycle stub implementation", header)
        self.assertIn("not", header)
        self.assertIn("frozen or backend-capable shared-library contract", header)
        self.assertNotIn("not yet an implemented shared-library contract", header)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4555 / V3 M156", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4555 C ABI header boundary refresh", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
