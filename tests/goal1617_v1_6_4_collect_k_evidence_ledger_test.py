from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1617_v1_6_4_collect_k_evidence_ledger_2026-05-09.md"


class Goal1617CollectKEvidenceLedgerTest(unittest.TestCase):
    def test_ledger_marks_two_goal1613_items_satisfied(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("PARTIALLY SATISFIED", text)
        self.assertIn("v1_6_x_collect_k_exact_bounds_stress_artifact", text)
        self.assertIn("v1_6_x_collect_k_prepared_output_reduced_copy_benchmark_package", text)
        self.assertIn("Satisfied for local fake-native scope", text)
        self.assertIn("rehearsed on local Linux all-backend scope", text)

    def test_ledger_keeps_representative_rtx_and_promotion_consensus_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("representative_rtx_collect_k_required_backend_performance_packet", text)
        self.assertIn("Not satisfied", text)
        self.assertIn("GTX 1070 behavior rehearsal only", text)
        self.assertIn("v1_6_x_collect_k_stable_promotion_3ai_consensus", text)
        self.assertIn("Stable promotion review must happen after representative RTX evidence", text)

    def test_ledger_points_to_pod_packet_plan(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal1616 is ready for the next paid pod window", text)
        self.assertIn("goal1616_v1_6_4_collect_k_rtx_packet_plan_2026-05-09.md", text)

    def test_ledger_claim_boundary_blocks_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not authorize stable", text)
        self.assertIn("public\nspeedup wording", text)
        self.assertIn("true zero-copy wording", text)
        self.assertIn("broad\nRTX/GPU wording", text)
        self.assertIn("release action", text)

    def test_external_reviews_and_consensus_accept_status_ledger(self) -> None:
        review_paths = (
            ROOT / "docs/reviews/goal1617_v1_6_4_collect_k_evidence_ledger_claude_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1617_v1_6_4_collect_k_evidence_ledger_gemini_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1617_v1_6_4_collect_k_evidence_ledger_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("Representative RTX required-backend evidence is not yet satisfied", consensus)
        self.assertIn("No speedup, zero-copy, stable promotion", consensus)


if __name__ == "__main__":
    unittest.main()
