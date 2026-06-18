from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4595_v3_0_m196_c_abi_prefix_stage_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4595_v3_0_m196_c_abi_prefix_stage_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
MAKEFILE = ROOT / "Makefile"
STAGING_CONTRACT = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md"
EMBEDDING_README = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/README.md"


class Goal4595V30M196CAbiPrefixStageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4595_m196_v3_c_abi_prefix_stage")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_prefix_stage_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_prefix_stage.goal4595.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_makefile_docs_and_pkg_config_contract_are_wired(self) -> None:
        makefile = MAKEFILE.read_text(encoding="utf-8")
        staging = STAGING_CONTRACT.read_text(encoding="utf-8")
        embedding = EMBEDDING_README.read_text(encoding="utf-8")
        self.assertIn("stage-c-api-prefix:", makefile)
        self.assertIn("C_API_PREFIX_STAGE_ROOT", makefile)
        self.assertIn("C_API_PREFIX ?= /usr/local", makefile)
        self.assertIn("/share/rtdl/examples", makefile)
        self.assertIn("make stage-c-api-prefix", staging)
        self.assertIn("DESTDIR/prefix-style", staging)
        self.assertIn("make stage-c-api-prefix", embedding)
        self.assertIn("build/c_api_prefix_stage/usr/local", embedding)

    def test_checked_in_prefix_stage_compiles_and_runs(self) -> None:
        smoke = self.checked_in["prefix_stage_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertEqual("/opt/rtdl", smoke["prefix"])
        self.assertTrue(smoke["make_result"]["ok"])
        self.assertTrue(smoke["compile_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("direct_link_ok 0.1.3 ok", smoke["run_result"]["stdout"])
        self.assertIn(smoke["prefix_dir"], smoke["cflags_result"]["stdout"])
        self.assertIn(smoke["prefix_dir"], smoke["libs_result"]["stdout"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4595 / V3 M196", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4595 C ABI prefix stage", INDEX.read_text(encoding="utf-8"))
        self.assertTrue(self.checked_in["claim_boundary"]["prefix_layout_stage_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "prefix_layout_stage_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
