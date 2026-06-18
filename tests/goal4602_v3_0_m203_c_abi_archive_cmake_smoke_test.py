from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4602_v3_0_m203_c_abi_archive_cmake_smoke_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4602_v3_0_m203_c_abi_archive_cmake_smoke_2026-06-17.md"
STAGING_CONTRACT = ROOT / "docs/learn/v3_0_c_abi_staging_contract.md"
EMBEDDING_README = ROOT / "examples/current/embedding/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4602V30M203CAbiArchiveCmakeSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4602_m203_v3_c_abi_archive_cmake_smoke")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_archive_cmake_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_archive_cmake_smoke.goal4602.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_archive_cmake_consumer_configures_builds_and_runs(self) -> None:
        smoke = self.checked_in["archive_cmake_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["cmake_config_exists"])
        self.assertTrue(smoke["configure_result"]["ok"])
        self.assertTrue(smoke["build_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("cmake_archive_direct_link_ok 0.1.3 ok", smoke["run_result"]["stdout"])

    def test_docs_name_extracted_archive_cmake_path(self) -> None:
        staging = STAGING_CONTRACT.read_text(encoding="utf-8")
        embedding = EMBEDDING_README.read_text(encoding="utf-8")
        for text in (staging, embedding):
            self.assertIn("rtdl-c-api-stage-0.1.3", text)
            self.assertIn("CMAKE_PREFIX_PATH", text)
        self.assertIn("extracted source-tree archive", staging)
        self.assertIn("movable source-tree archive", embedding)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4602 / V3 M203", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4602 C ABI archive CMake smoke", INDEX.read_text(encoding="utf-8"))
        self.assertTrue(self.checked_in["claim_boundary"]["archive_cmake_stage_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "archive_cmake_stage_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
