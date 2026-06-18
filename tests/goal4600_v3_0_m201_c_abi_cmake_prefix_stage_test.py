from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4600_v3_0_m201_c_abi_cmake_prefix_stage_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4600_v3_0_m201_c_abi_cmake_prefix_stage_2026-06-17.md"
CMAKE_CONFIG = ROOT / "packaging/rtdl-c-api-config.cmake"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4600V30M201CAbiCmakePrefixStageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4600_m201_v3_c_abi_cmake_prefix_stage")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_cmake_prefix_stage_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_cmake_prefix_stage.goal4600.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_cmake_consumer_configures_builds_and_runs(self) -> None:
        smoke = self.checked_in["cmake_prefix_stage_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["configure_result"]["ok"])
        self.assertTrue(smoke["build_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("cmake_direct_link_ok 0.1.3 ok", smoke["run_result"]["stdout"])

    def test_cmake_config_exports_relocatable_imported_target(self) -> None:
        config = CMAKE_CONFIG.read_text(encoding="utf-8")
        self.assertIn("CMAKE_CURRENT_LIST_DIR", config)
        self.assertIn("add_library(rtdl::c_api SHARED IMPORTED)", config)
        self.assertIn("INTERFACE_INCLUDE_DIRECTORIES", config)
        self.assertIn("IMPORTED_LOCATION", config)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4600 / V3 M201", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4600 C ABI CMake prefix stage", INDEX.read_text(encoding="utf-8"))
        self.assertTrue(self.checked_in["claim_boundary"]["cmake_prefix_stage_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "cmake_prefix_stage_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
