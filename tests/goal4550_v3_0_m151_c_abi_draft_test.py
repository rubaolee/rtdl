from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "include/rtdl/rtdl.h"
DOC = ROOT / "docs/learn/v3_0_c_abi_draft.md"
PACKET = ROOT / "docs/reports/goal4550_v3_0_m151_c_abi_draft_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4550_v3_0_m151_c_abi_draft_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4550V30M151CAbiDraftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4550_m151_v3_c_abi_draft")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_c_abi_draft_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_draft.goal4550.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_header_is_c_only_opaque_boundary(self) -> None:
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn('extern "C"', header)
        self.assertIn("typedef struct rtdl_context rtdl_context;", header)
        self.assertIn("typedef struct rtdl_buffer_view", header)
        self.assertIn("void* stream", header)
        self.assertNotIn("class ", header)
        self.assertNotIn("template<", header)
        self.assertNotIn("std::", header)

    def test_docs_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("not an implemented shared-library ABI", DOC.read_text(encoding="utf-8"))
        self.assertIn("Goal4550 / V3 M151", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4550 C ABI draft", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
