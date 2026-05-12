from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1683_consensus_audit_remediation_plan_2026-05-11.md"
DATA = ROOT / "docs" / "reports" / "goal1683_consensus_audit_remediation_plan_2026-05-11.json"
SOURCE = ROOT / "docs" / "reports" / "goal_consensus_audit_since_v0_15_2026-05-11.json"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal1684_gemini_review_goals1668_1682_2026-05-11.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal1685_claude_review_goals1668_1682_2026-05-11.md"
CLAUDE_FOLLOWUP = ROOT / "docs" / "reviews" / "goal1685_followup_claude_fresh_review_goals1681_1682_2026-05-11.md"
RECONCILIATION = ROOT / "docs" / "reviews" / "goal1687_goals1668_1682_distinct_ai_consensus_reconciliation_2026-05-11.md"


class Goal1683ConsensusAuditRemediationPlanTest(unittest.TestCase):
    def test_source_audit_counts_are_preserved(self) -> None:
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(data["source_boundary_used"], source["boundary"])
        self.assertEqual(data["source_counts"]["passing"], len(source["passing"]))
        self.assertEqual(data["source_counts"]["missing_or_invalid"], len(source["missing_or_invalid"]))
        self.assertEqual(data["source_counts"]["ambiguous"], len(source["ambiguous"]))
        self.assertEqual(data["source_counts"], {
            "passing": 80,
            "missing_or_invalid": 98,
            "ambiguous": 351,
        })

    def test_codex_cannot_close_distinct_ai_consensus_alone(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        rule = data["consensus_rule"]
        self.assertEqual(rule["minimum_ai_reviews"], 2)
        self.assertTrue(rule["distinct_ai_systems_required"])
        self.assertFalse(rule["codex_plus_codex_valid"])
        self.assertTrue(rule["authoring_is_not_independent_review"])
        self.assertIn("Codex alone cannot close", data["codex_remediation_verdict"])

    def test_current_release_blockers_include_current_goal_chain(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        blockers = data["current_release_blockers"]
        self.assertEqual(blockers["ambiguous_from_gemini_audit"], [1668, 1669, 1670])
        self.assertEqual(blockers["not_covered_by_gemini_audit"], list(range(1671, 1683)))
        self.assertEqual(blockers["missing_or_invalid_if_used_as_release_evidence"], [1649])

    def test_report_blocks_release_use_until_external_reviews_exist(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Codex cannot close distinct-AI consensus gaps by itself",
            "Codex + Codex",
            "Goals1668-1682",
            "goal1684_gemini_review_goals1668_1682_2026-05-11.md",
            "goal1685_claude_review_goals1668_1682_2026-05-11.md",
            "goal1685_followup_claude_fresh_review_goals1681_1682_2026-05-11.md",
            "using any of the 98 missing/invalid goals as release evidence",
            "using Goals1671-1682 as final v1.8/v2.0 release evidence",
            "Claude + Gemini",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_external_reviews_are_reconciled_with_claude_authoring_caveat(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        status = data["current_external_review_status"]["goals1668_1682"]
        self.assertEqual(
            status["gemini_review"]["path"],
            "docs/reviews/goal1684_gemini_review_goals1668_1682_2026-05-11.md",
        )
        self.assertEqual(status["gemini_review"]["status"], "complete")
        self.assertTrue(status["gemini_review"]["independent"])
        self.assertEqual(
            status["claude_review"]["path"],
            "docs/reviews/goal1685_claude_review_goals1668_1682_2026-05-11.md",
        )
        self.assertEqual(status["claude_review"]["status"], "complete_with_independence_caveat")
        self.assertEqual(status["claude_review"]["independent_for_goals"], list(range(1668, 1681)))
        self.assertEqual(status["claude_review"]["not_fully_independent_for_goals"], [1681, 1682])
        followup = status["claude_followup_review_goals1681_1682"]
        self.assertEqual(
            followup["path"],
            "docs/reviews/goal1685_followup_claude_fresh_review_goals1681_1682_2026-05-11.md",
        )
        self.assertEqual(
            followup["status"],
            "complete_as_compatibility_audit_with_same_conversation_independence_caveat",
        )
        self.assertEqual(followup["verdicts"]["Goal1681"], "accept-with-boundary")
        self.assertEqual(followup["verdicts"]["Goal1682"], "accept-with-boundary")
        self.assertEqual(followup["verdicts"]["overall_v1_8_v2_0"], "needs-more-evidence")
        self.assertEqual(
            followup["strict_consensus_effect"],
            "does_not_close_fresh_non_authoring_review_requirement",
        )
        self.assertEqual(
            status["reconciliation"],
            "docs/reviews/goal1687_goals1668_1682_distinct_ai_consensus_reconciliation_2026-05-11.md",
        )
        self.assertEqual(
            status["consensus_status"],
            "goals1668_1680_clean_goals1681_1682_need_fresh_independent_review",
        )

        review_text = GEMINI_REVIEW.read_text(encoding="utf-8")
        for phrase in (
            "independent Gemini review",
            "Codex+Codex",
            "needs-more-evidence",
            "Full v1.8/v2.0 release readiness remains gated",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, review_text)

        claude_text = CLAUDE_REVIEW.read_text(encoding="utf-8")
        for phrase in (
            "distinct AI system",
            "Codex + Codex",
            "not fully independent",
            "Goal1681 and Goal1682",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, claude_text)

        followup_text = CLAUDE_FOLLOWUP.read_text(encoding="utf-8")
        for phrase in (
            "Stale string-literal references to the old ABI names",
            "Python compatibility surface preserved",
            "Strict cross-session non-authoring Claude independence",
            "Goal1681 verdict: `accept-with-boundary`",
            "Goal1682 verdict: `accept-with-boundary`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, followup_text)

        reconciliation_text = RECONCILIATION.read_text(encoding="utf-8")
        for phrase in (
            "Goals1668-1680 now have distinct external Gemini + Claude review coverage",
            "Goals1681 and 1682 do not yet have strict distinct-AI consensus",
            "old PIP/Hausdorff native ABI references are gone from the",
            "fresh review from a Claude",
            "session that did not author those migrations",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, reconciliation_text)


if __name__ == "__main__":
    unittest.main()
