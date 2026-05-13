from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reviews" / "goal1813_3ai_consensus_v2_0_release_readiness_2026-05-13.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal1811_claude_review_goal1810_v2_0_release_readiness_audit_2026-05-13.md"
GEMINI = ROOT / "docs" / "reviews" / "goal1812_gemini_review_goal1810_v2_0_release_readiness_audit_2026-05-13.md"


class Goal1813V20ReleaseReadinessConsensusTest(unittest.TestCase):
    def test_consensus_has_distinct_external_inputs_and_is_superseded(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("Verdict: `superseded-by-goal1814`", text)
        self.assertIn("Claude:", text)
        self.assertIn("Gemini:", text)
        self.assertIn("Both external systems are distinct from Codex", text)
        self.assertIn("Codex+Codex is not counted", text)
        self.assertIn("no longer authorizes a v2.0 release", text)

    def test_consensus_records_allowed_and_blocked_claims(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("RTDL v2.0 introduces the first Python+partner+RTDL path", text)
        self.assertIn("host-stage bridge", text)
        for blocked in (
            "true zero-copy",
            "direct device-pointer handoff",
            "broad RT-core speedup",
            "whole-application acceleration",
            "packaging/install support beyond source-tree execution",
        ):
            with self.subTest(blocked=blocked):
                self.assertIn(blocked, text)

    def test_consensus_requires_user_authorization_before_publish(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("does not tag, publish, or move a release", text)
        self.assertIn("stricter blockers are solved", text)

    def test_external_reviews_exist_and_accept_with_boundary(self) -> None:
        for path in (CLAUDE, GEMINI):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("accept-with-boundary", text)


if __name__ == "__main__":
    unittest.main()
