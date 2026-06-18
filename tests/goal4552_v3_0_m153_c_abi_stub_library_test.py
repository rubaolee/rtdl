from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/native/rtdl_c_api.cpp"
PACKET = ROOT / "docs/reports/goal4552_v3_0_m153_c_abi_stub_library_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4552_v3_0_m153_c_abi_stub_library_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4552V30M153CAbiStubLibraryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4552_m153_v3_c_abi_stub_library")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_stub_source_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_stub_library.goal4552.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_shared_library_smoke_passed(self) -> None:
        build_result = self.checked_in["build_result"]
        self.assertTrue(build_result["ok"])
        self.assertTrue(build_result["ctypes_smoke"]["ok"])
        self.assertTrue(self.checked_in["checks"]["shared_library_build_ok"])
        self.assertTrue(self.checked_in["checks"]["ctypes_smoke_ok"])

    def test_source_boundaries_and_report_are_wired(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn('#include "rtdl/rtdl.h"', source)
        self.assertIn("rtdl_context_create", source)
        self.assertIn("rtdl_buffer_import", source)
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4552 / V3 M153", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4552 C ABI stub library", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
