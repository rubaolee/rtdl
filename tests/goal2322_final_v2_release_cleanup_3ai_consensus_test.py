from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2322_final_v2_0_release_cleanup_3ai_consensus_2026-05-18.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal2320_claude_final_v2_0_release_cleanup_review_2026-05-18.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2321_gemini_final_v2_0_release_cleanup_review_2026-05-18.md"


class Goal2322FinalV2ReleaseCleanup3AIConsensusTest(unittest.TestCase):
    def test_external_reviews_exist_and_accept_with_boundary(self) -> None:
        self.assertIn("accept-with-boundary", CLAUDE.read_text(encoding="utf-8").lower())
        self.assertIn("accept-with-boundary", GEMINI.read_text(encoding="utf-8").lower())

    def test_consensus_records_distinct_ai_families(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for phrase in (
            "Codex",
            "Claude",
            "Gemini",
            "distinct external AI families",
            "Codex+Codex is not counted",
            "`accept-with-boundary`",
        ):
            self.assertIn(phrase, text)

    def test_consensus_preserves_claim_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for phrase in (
            "package-install or PyPI support",
            "arbitrary PyTorch/CuPy acceleration",
            "broad RT-core speedup",
            "whole-application speedup",
            "arbitrary polygon overlay",
            "RTDL-beats-RayJoin",
            "version/tag/publish action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
