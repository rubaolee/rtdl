from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1621_v1_6_4_collect_k_evidence_ledger_after_rtx_2026-05-09.md"


class Goal1621CollectKEvidenceLedgerAfterRtxTest(unittest.TestCase):
    def test_ledger_marks_rtx_packet_evidence_satisfied(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RTX PACKET EVIDENCE SATISFIED", text)
        self.assertIn("representative_rtx_collect_k_required_backend_performance_packet", text)
        self.assertIn("Satisfied as required-backend packet-execution evidence", text)
        self.assertIn("goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_2026-05-09.md", text)

    def test_ledger_keeps_stable_promotion_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Stable `COLLECT_K_BOUNDED` promotion remains blocked", text)
        self.assertIn("v1_6_x_collect_k_stable_promotion_3ai_consensus", text)
        self.assertIn("Not satisfied", text)
        self.assertIn("fresh 3-AI review", text)

    def test_ledger_claim_boundary_blocks_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("true zero-copy wording", text)
        self.assertIn("broad RTX/GPU wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED`\npromotion", text)
        self.assertIn("release action", text)

    def test_external_reviews_and_consensus_accept_after_rtx_ledger_only(self) -> None:
        review_paths = (
            ROOT
            / "docs/reviews/goal1621_v1_6_4_collect_k_evidence_ledger_after_rtx_claude_review_2026-05-09.md",
            ROOT
            / "docs/reviews/goal1621_v1_6_4_collect_k_evidence_ledger_after_rtx_gemini_review_2026-05-09.md",
            ROOT
            / "docs/reviews/goal1621_v1_6_4_collect_k_evidence_ledger_after_rtx_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("Representative RTX A4500 required-backend packet-execution evidence is\n  satisfied", consensus)
        self.assertIn("Stable `COLLECT_K_BOUNDED` promotion is not satisfied", consensus)


if __name__ == "__main__":
    unittest.main()
