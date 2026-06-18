from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/README.md"
PACKET = ROOT / "docs/reports/goal4560_v3_0_m161_c_abi_embedding_readme_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4560_v3_0_m161_c_abi_embedding_readme_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4560V30M161CAbiEmbeddingReadmeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4560_m161_v3_c_abi_embedding_readme")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_readme_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_embedding_readme.goal4560.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_readme_contains_commands_and_boundaries(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("make build-c-api", readme)
        self.assertIn("hit_count=1 first_pair=(0,0)", readme)
        self.assertIn("not an OptiX, Embree, device-buffer", readme)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4560 / V3 M161", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4560 C ABI embedding README", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
