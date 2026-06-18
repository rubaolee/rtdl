from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4586_v3_0_m187_c_abi_pkg_config_relocatable_stage_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4586_v3_0_m187_c_abi_pkg_config_relocatable_stage_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4586V30M187CAbiPkgConfigRelocatableStageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4586_m187_v3_c_abi_pkg_config_relocatable_stage")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_pkg_config_relocatable_stage_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_pkg_config_relocatable_stage.goal4586.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_relocated_stage_compiles_and_runs_direct_link_client(self) -> None:
        smoke = self.checked_in["relocatable_stage_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["compile_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("direct_link_ok 0.1.3 ok", smoke["run_result"]["stdout"])
        self.assertIn(smoke["copied_stage_dir"], smoke["cflags_result"]["stdout"])
        self.assertIn(smoke["copied_stage_dir"], smoke["libs_result"]["stdout"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4586 / V3 M187", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4586 C ABI pkg-config relocatable stage", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
