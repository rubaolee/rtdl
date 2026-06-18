from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4577_v3_0_m178_c_abi_pkg_config_stage_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4577_v3_0_m178_c_abi_pkg_config_stage_2026-06-17.md"
PC_TEMPLATE = ROOT / "packaging/rtdl-c-api.pc"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4577V30M178CAbiPkgConfigStageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4577_m178_v3_c_abi_pkg_config_stage")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_pkg_config_stage_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_pkg_config_stage.goal4577.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_direct_link_smoke_passed(self) -> None:
        smoke = self.checked_in["pkg_config_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["cflags_result"]["ok"])
        self.assertTrue(smoke["libs_result"]["ok"])
        self.assertTrue(smoke["compile_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("direct_link_ok 0.1.2 ok", smoke["run_result"]["stdout"])

    def test_template_report_index_and_boundaries_are_wired(self) -> None:
        template = PC_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("prefix=${pcfiledir}/../..", template)
        self.assertIn("Version: 0.1.2", template)
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4577 / V3 M178", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4577 C ABI pkg-config stage", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
