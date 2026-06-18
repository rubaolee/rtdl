from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4576_v3_0_m177_c_abi_staging_bundle_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4576_v3_0_m177_c_abi_staging_bundle_2026-06-17.md"
MAKEFILE = ROOT / "Makefile"
STAGING_DOC = ROOT / "docs/learn/v3_0_c_abi_staging_contract.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4576V30M177CAbiStagingBundleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4576_m177_v3_c_abi_staging_bundle")
        cls.packet = cls.module.build_packet(ROOT, run_make=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_staging_bundle_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_staging_bundle.goal4576.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_stage_run_built_and_ran_example(self) -> None:
        stage = self.checked_in["stage_result"]
        self.assertTrue(stage["ok"])
        self.assertTrue(stage["make_result"]["ok"])
        self.assertTrue(stage["compile_result"]["ok"])
        self.assertTrue(stage["run_result"]["ok"])
        self.assertEqual("hit_count=1 first_pair=(0,0)", stage["run_result"]["stdout"])
        self.assertEqual("0.1.3", stage["staged_manifest"]["abi_version"])

    def test_makefile_docs_report_index_and_boundaries_are_wired(self) -> None:
        self.assertIn("stage-c-api:", MAKEFILE.read_text(encoding="utf-8"))
        self.assertIn("build/c_api_stage", STAGING_DOC.read_text(encoding="utf-8"))
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4576 / V3 M177", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4576 C ABI staging bundle", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
