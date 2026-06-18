from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4544_v3_0_m145_app_author_strategy_doc_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4544_v3_0_m145_app_author_strategy_doc_2026-06-17.md"
DOC = ROOT / "docs/learn/v3_0_app_author_implementation_strategy.md"
LEARN_INDEX = ROOT / "docs/learn/README.md"


class Goal4544V30M145AppAuthorStrategyDocTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4544_m145_v3_app_author_strategy_doc")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_strategy_doc_checks_all_pass(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.app_author_strategy_doc.goal4544.v1",
            self.packet["version"],
        )
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doc_has_current_v3_strategy_and_all_apps(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for label in self.module.REQUIRED_APP_LABELS:
            self.assertIn(label, text)
        self.assertIn("Goal4614", text)
        self.assertIn("Goal4543", text)
        self.assertIn("V4 deferrals", text)
        self.assertIn("RTDL does not promise miracles", text)
        self.assertIn("Do not expose arbitrary raw callbacks", text)
        self.assertIn("RT-native hierarchical traversal is not implemented", text)

    def test_links_and_report_are_wired(self) -> None:
        learn_index = LEARN_INDEX.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("V3.0 App-Author Implementation Strategy", learn_index)
        self.assertIn("Goal4544 / V3 M145", report)
        self.assertIn("No runtime was executed", report)

    def test_claim_boundary_remains_blocked(self) -> None:
        for key, value in self.packet["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
