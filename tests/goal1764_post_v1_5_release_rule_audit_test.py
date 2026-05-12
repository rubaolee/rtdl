import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1764_post_v1_5_release_rule_audit_2026-05-12.md"


class Goal1764PostV15ReleaseRuleAuditTest(unittest.TestCase):
    def test_audit_verdict_and_scope_are_explicit(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("post_v1_5_release_rule_audit_passes_for_v1_8_with_historical_quarantine", text)
        self.assertIn("all release-used post-v1.5 material is consensus-clean", text)
        self.assertIn("all other post-v1.5 material is quarantined from release claims", text)

    def test_broad_audit_counts_are_not_ignored(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("goal_consensus_audit_since_v0_15_2026-05-11.md", text)
        self.assertIn("`v1.5` tag", text)
        self.assertIn("Passing | 80", text)
        self.assertIn("Missing or invalid | 98", text)
        self.assertIn("Ambiguous | 351", text)
        self.assertIn("Those counts are not ignored", text)

    def test_release_used_reviews_and_consensus_files_exist(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        required = (
            "docs/reviews/goal1738_claude_review_goal1737_v1_8_gap_audit_2026-05-12.md",
            "docs/reviews/goal1739_gemini_review_goal1737_v1_8_gap_audit_2026-05-12.md",
            "docs/reviews/goal1743_gemini_review_goal1742_v1_8_release_candidate_packet_2026-05-12.md",
            "docs/reviews/goal1745_gemini_second_pass_review_goal1742_v1_8_release_candidate_packet_2026-05-12.md",
            "docs/reviews/goal1751_gemini_review_goal1750_same_contract_perf_summary_2026-05-12.md",
            "docs/reviews/goal1760_claude_review_goal1759_v1_8_release_prep_2026-05-12.md",
            "docs/reviews/goal1761_gemini_review_goal1759_v1_8_release_prep_2026-05-12.md",
            "docs/reports/goal1762_v1_8_final_release_prep_consensus_2026-05-12.md",
        )
        for rel in required:
            with self.subTest(rel=rel):
                self.assertIn(rel, text)
                self.assertTrue((ROOT / rel).exists(), rel)

    def test_quarantine_rule_blocks_unreviewed_historical_goals_from_release_use(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("release-quarantined by default", text)
        self.assertIn("cannot be used for v1.8 public release claims", text)
        self.assertIn("distinct-AI review", text)
        self.assertIn("Codex+Codex is not valid consensus", text)


if __name__ == "__main__":
    unittest.main()
