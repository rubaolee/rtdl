from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4585_v3_0_m186_c_abi_staging_inventory_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4585_v3_0_m186_c_abi_staging_inventory_refresh_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4585V30M186CAbiStagingInventoryRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4585_m186_v3_c_abi_staging_inventory_refresh")
        cls.packet = cls.module.build_packet(ROOT, run_stage=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_staging_inventory_refresh_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_staging_inventory_refresh.goal4585.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_stage_inventory_contains_all_current_examples(self) -> None:
        inventory = self.checked_in["stage_inventory"]
        self.assertTrue(inventory["ok"])
        self.assertTrue(inventory["stage_result"]["ok"])
        self.assertTrue(inventory["all_examples_staged"])
        for name in self.checked_in["examples"]:
            item = inventory["staged_examples"][name]
            self.assertTrue(item["exists"], name)
            self.assertGreater(item["size_bytes"], 0, name)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4585 / V3 M186", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4585 C ABI staging inventory refresh", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
