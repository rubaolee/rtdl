from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs/reports/goal4270_v2_10_milestone_release_3ai_consensus_2026-06-10.md"
CLAUDE = ROOT / "docs/reviews/goal4268_claude_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md"
GEMINI = ROOT / "docs/reviews/goal4269_gemini_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md"


class Goal4270V210MilestoneReleaseConsensusTest(unittest.TestCase):
    @staticmethod
    def _flat(text: str) -> str:
        return " ".join(text.split())

    def test_consensus_has_distinct_external_accepts(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Claude", text)
        self.assertIn("Gemini", text)
        self.assertIn("two distinct external AI reviewers", text)
        self.assertIn("Verdict: **accept**", claude)
        self.assertIn("Verdict: `accept`", gemini)

    def test_consensus_authorizes_only_source_tree_milestone_tag(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Create and push the `v2.10` source-tree milestone tag", text)
        self.assertIn("source-tree milestone", text)
        self.assertIn("0c842eb0", text)
        self.assertIn("final delta after `0c842eb0` is", text)

    def test_consensus_records_validation_without_fake_pod_claim(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        flat = self._flat(text)

        self.assertIn("Ran 20 tests", text)
        self.assertIn("OK", text)
        self.assertIn("refused the SSH connection", text)
        self.assertIn("does not claim a fresh pod run", flat)

    def test_consensus_preserves_blocked_claims(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        flat = self._flat(text)

        for phrase in (
            "package-install wording",
            "broad speedup wording",
            "whole-app acceleration wording",
            "broad RT-core wording",
            "RTDL-beats-RayJoin wording",
            "paper-reproduction wording",
            "true-zero-copy wording",
            "automatic backend/partner selection wording",
            "AMD/HIPRT performance wording",
            "Embree+Numba CPU partner wording",
            "app-specific native-engine logic",
            "universal CuPy-vs-Numba winner wording",
        ):
            self.assertIn(phrase, flat)


if __name__ == "__main__":
    unittest.main()
