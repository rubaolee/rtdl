from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4414_v3_0_midterm_review_packet_2026-06-15.md"
CONSENSUS = ROOT / "docs/reports/goal4414_v3_0_midterm_3ai_consensus_2026-06-15.md"
CLAUDE_HANDOFF = ROOT / "docs/handoff/HANDOFF_CLAUDE_GOAL4414_V3_0_MIDTERM_REVIEW_2026-06-15.md"
GEMINI_HANDOFF = ROOT / "docs/handoff/HANDOFF_GEMINI_GOAL4414_V3_0_MIDTERM_REVIEW_2026-06-15.md"
CLAUDE_REVIEW = ROOT / "docs/reviews/goal4414_claude_review_v3_0_midterm_2026-06-15.md"
GEMINI_REVIEW = ROOT / "docs/reviews/goal4414_gemini_review_v3_0_midterm_2026-06-15.md"


class Goal4414V30Midterm3AIConsensusTest(unittest.TestCase):
    def test_midterm_packet_records_m1_to_m17_scope_and_next_target(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        self.assertIn("Current commit under review: `7ab19f4a`", text)
        self.assertIn("M17 partner-device prepare", text)
        self.assertIn("M18 device-side grouped contract", text)
        self.assertIn("Unsupported Claims", text)
        self.assertIn("public V3 performance claims", text)
        self.assertIn("grouped argmin over device-only prepared ray batches", text)

    def test_handoffs_request_independent_external_reviews(self) -> None:
        for path, reviewer in ((CLAUDE_HANDOFF, "Claude"), (GEMINI_HANDOFF, "Gemini")):
            text = path.read_text(encoding="utf-8")
            self.assertIn(reviewer, text)
            self.assertIn("goal4414_v3_0_midterm_review_packet_2026-06-15.md", text)
            self.assertIn("accept-with-boundary", text)
            self.assertIn("needs-more-evidence", text)
            self.assertIn("Do not edit files", text)
            self.assertIn("Do not authorize public performance", text)

    def test_external_reviews_accept_with_boundary_and_keep_claims_blocked(self) -> None:
        for path, reviewer in ((CLAUDE_REVIEW, "Claude"), (GEMINI_REVIEW, "Gemini")):
            text = path.read_text(encoding="utf-8")
            self.assertIn(reviewer, text)
            self.assertIn("accept-with-boundary", text)
            self.assertIn("Blocking Findings", text)
            self.assertIn("M18", text)
            self.assertIn("No public", text)
            self.assertIn("zero-copy", text)

    def test_consensus_records_three_accepts_and_m18_guardrails(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("v3_0_midterm_accepted_m18_device_side_grouped_contract_allowed", text)
        self.assertIn("| Codex | `accept-with-boundary` | 0 |", text)
        self.assertIn("| Claude | `accept-with-boundary` | 0 |", text)
        self.assertIn("| Gemini | `accept-with-boundary` | 0 |", text)
        self.assertIn("CuPy best-partner and Numba reference rows", text)
        self.assertIn("hit-stream Numba gap", text)
        self.assertIn("transfer-counter methodology limits", text)
        self.assertIn("measured-window no-hidden-copy", text)
        self.assertIn("not a release, benchmark, or public performance gate", text)

    def test_consensus_does_not_replace_external_reviews_with_subagent(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("not counted as a Claude/Gemini substitute", text)


if __name__ == "__main__":
    unittest.main()
