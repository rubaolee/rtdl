from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2187_rayjoin_phase0_external_consensus_2026-05-17.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2185_gemini_review_goal2184_rayjoin_phase0_2026-05-17.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal2186_claude_review_goal2184_rayjoin_phase0_2026-05-17.md"


class Goal2187RayjoinPhase0ExternalConsensusTest(unittest.TestCase):
    def test_consensus_records_distinct_external_reviews(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")
        claude = CLAUDE.read_text(encoding="utf-8")

        self.assertIn("3-AI consensus", text)
        self.assertIn("Gemini", text)
        self.assertIn("Claude", text)
        self.assertIn("accept-with-boundary", gemini)
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("Reviewer: Claude", claude)
        self.assertIn("Gemini Review", gemini)

    def test_consensus_accepts_only_local_phase(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("local source/protocol/sample lane", text)
        self.assertIn("RayJoin sample overlay", text)
        self.assertIn("RTDL v2.0 bounded same-sample", text)
        self.assertIn("does not authorize", text)
        self.assertIn("full RayJoin paper reproduction claims", text)
        self.assertIn("claims that RTDL beats RayJoin", text)
        self.assertIn("v2.0 release authorization", text)

    def test_consensus_records_metadata_correction_and_next_pod_gate(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn('"goal": "2159"', text)
        self.assertIn('"goal": "2184"', text)
        self.assertIn("RTX pod", text)
        self.assertIn("RTX-era SM target", text)
        self.assertIn("CUDA/CuPy spatial baselines", text)


if __name__ == "__main__":
    unittest.main()
