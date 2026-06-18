from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4565_v3_0_m166_c_abi_stability_policy_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4565_v3_0_m166_c_abi_stability_policy_2026-06-17.md"
POLICY = ROOT / "docs/learn/v3_0_c_abi_stability_policy.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4565V30M166CAbiStabilityPolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4565_m166_v3_c_abi_stability_policy")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_policy_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_stability_policy.goal4565.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_policy_blocks_stable_wording_until_gated(self) -> None:
        text = POLICY.read_text(encoding="utf-8")
        self.assertIn("not frozen", text)
        self.assertIn("Until those gates pass", text)
        self.assertIn("never stable SDK", text)
        self.assertIn("Cross-version compatibility tests", text)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4565 / V3 M166", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4565 C ABI stability policy", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
