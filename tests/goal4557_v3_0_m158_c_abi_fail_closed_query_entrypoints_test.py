from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "include/rtdl/rtdl.h"
SOURCE = ROOT / "src/native/rtdl_c_api.cpp"
PACKET = ROOT / "docs/reports/goal4557_v3_0_m158_c_abi_fail_closed_query_entrypoints_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4557_v3_0_m158_c_abi_fail_closed_query_entrypoints_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4557V30M158CAbiFailClosedQueryEntryPointsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4557_m158_v3_c_abi_fail_closed_query_entrypoints")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_query_entrypoint_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_fail_closed_query_entrypoints.goal4557.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_header_and_stub_are_fail_closed(self) -> None:
        header = HEADER.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("rtdl_index_build", header)
        self.assertIn("rtdl_query_execute", header)
        self.assertIn("RTDL_STATUS_ERROR_UNSUPPORTED", source)
        self.assertIn("not implemented in the lifecycle stub", source)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4557 / V3 M158", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4557 C ABI fail-closed query entrypoints", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
