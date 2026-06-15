from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/reports/goal4405_v3_0_m10_same_stream_evidence_plan_2026-06-15.md"
HANDOFF = ROOT / "docs/handoff/HANDOFF_3AI_GOAL4405_V3_0_M10_SAME_STREAM_EVIDENCE_PLAN_2026-06-15.md"
CODEX = ROOT / "docs/reviews/goal4405_codex_review_v3_0_m10_same_stream_evidence_plan_2026-06-15.md"
CLAUDE = ROOT / "docs/reviews/goal4405_claude_review_v3_0_m10_same_stream_evidence_plan_2026-06-15.md"
GEMINI = ROOT / "docs/reviews/goal4405_gemini_review_v3_0_m10_same_stream_evidence_plan_2026-06-15.md"
CONSENSUS = ROOT / "docs/reports/goal4405_3ai_consensus_v3_0_m10_same_stream_evidence_plan_2026-06-15.md"


class Goal4405V30M10SameStreamConsensusTest(unittest.TestCase):
    def test_review_packet_files_exist(self) -> None:
        for path in (PLAN, HANDOFF, CODEX, CLAUDE, GEMINI, CONSENSUS):
            self.assertTrue(path.exists(), f"missing {path}")

    def test_plan_is_evidence_gate_not_public_claim(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        for phrase in (
            "M10 is a narrow evidence gate",
            "It is not a benchmark-app speedup result",
            "same_stream_ready=false",
            "true_zero_copy_ready=false",
            "Failing closed is an acceptable M10 result. Faking readiness is not.",
            "Pointer identity alone is not enough.",
            "public_claim_authorized=false",
        ):
            self.assertIn(phrase, text)

    def test_plan_requires_exact_evidence_for_same_stream_and_zero_copy(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        for phrase in (
            "observed `cuda_event_pair` or `nsight_stream_correlation`",
            "native producer and partner consumer",
            "transfer-counter or equivalent no-hidden-copy evidence",
            "`host_materialized=false`",
            "`hidden_copy_observed=false`",
            "If the native wrapper synchronizes internally",
        ):
            self.assertIn(phrase, text)

    def test_reviews_accept_with_gates(self) -> None:
        for path in (CODEX, CLAUDE, GEMINI):
            text = path.read_text(encoding="utf-8")
            match = re.search(r"^VERDICT: (ACCEPT|ACCEPT_WITH_GATES|REQUEST_CHANGES)$", text, re.MULTILINE)
            self.assertIsNotNone(match, f"{path} must contain an exact verdict line")
            self.assertEqual("ACCEPT_WITH_GATES", match.group(1))

    def test_consensus_allows_m10_but_keeps_claims_false(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        for phrase in (
            "v3_0_m10_same_stream_evidence_allowed_fail_closed_required",
            "M10 same-stream evidence implementation may begin",
            "No reviewer returned `REQUEST_CHANGES`",
            "`same_stream_ready=true` requires observed `cuda_event_pair`",
            "Pointer identity alone is not enough",
            "All public claim booleans remain false",
            "every claim boundary remains false",
        ):
            self.assertIn(phrase, text)

    def test_consensus_requires_both_partners_and_threshold7(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("CuPy and Numba rows are both required", text)
        self.assertIn("threshold-7 predicated case remains required", text)
        self.assertIn("automatic partner/backend selection", text)


if __name__ == "__main__":
    unittest.main()
