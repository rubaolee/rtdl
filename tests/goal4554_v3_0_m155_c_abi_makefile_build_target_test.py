from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"
PACKET = ROOT / "docs/reports/goal4554_v3_0_m155_c_abi_makefile_build_target_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4554_v3_0_m155_c_abi_makefile_build_target_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4554V30M155CAbiMakefileBuildTargetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4554_m155_v3_c_abi_makefile_build_target")
        cls.packet = cls.module.build_packet(ROOT, run_make=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_makefile_wiring_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_makefile_build_target.goal4554.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_make_build_passed_on_pod(self) -> None:
        make_result = self.checked_in["make_result"]
        self.assertTrue(make_result["ok"])
        self.assertTrue(make_result["artifact_exists"])
        self.assertGreater(make_result["artifact_size_bytes"], 0)
        self.assertTrue(self.checked_in["checks"]["make_build_c_api_ok"])

    def test_makefile_report_index_and_boundaries_are_wired(self) -> None:
        makefile = MAKEFILE.read_text(encoding="utf-8")
        self.assertIn("build-c-api:", makefile)
        self.assertIn("src/native/rtdl_c_api.cpp", makefile)
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4554 / V3 M155", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4554 C ABI Makefile build target", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
