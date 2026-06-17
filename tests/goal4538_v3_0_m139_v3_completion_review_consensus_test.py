from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4538V30M139CompletionReviewConsensusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4538_m139_v3_completion_review_consensus")
        cls.packet = cls.module.build_packet()
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_consensus_checks_all_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.completion_review_consensus.goal4538.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_three_ai_verdicts_have_no_blocking_findings(self) -> None:
        reviewers = {row["reviewer"]: row for row in self.packet["reviewers"]}
        self.assertEqual(
            {"codex_local_self_review", "harvey_external_review", "pascal_external_review"},
            set(reviewers),
        )
        self.assertEqual("approve", reviewers["harvey_external_review"]["verdict"])
        self.assertEqual("approve_with_caveats", reviewers["pascal_external_review"]["verdict"])
        for row in reviewers.values():
            self.assertEqual((), tuple(row["blocking_findings"]), row["reviewer"])
            self.assertIn(row["verdict"], {"approve", "approve_with_caveats"})

    def test_completion_claim_stays_narrow(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("V3 current benchmark-app implementation queue is complete", report)
        self.assertIn("Goal4540 later supersedes the Triangle future-design classification", report)
        self.assertIn("Goal4541 later closes Barnes-Hut", report)
        self.assertIn("all ten apps are closed current targets", report)
        self.assertIn("No release, public speedup, broad RT-core", report)
        self.assertNotIn("V3 release complete", report)
        self.assertNotIn("RT-native Barnes-Hut/Triangle complete", report)

    def test_checked_in_packet_and_index_are_wired(self) -> None:
        index = INDEX.read_text(encoding="utf-8")
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertEqual("approve_with_caveats", self.checked_in["consensus_verdict"])
        self.assertIn("Goal4538 V3 completion review consensus", index)


if __name__ == "__main__":
    unittest.main()
