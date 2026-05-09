from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1624_v1_6_4_collect_k_stable_promotion_decision_2026-05-09.md"


class Goal1624CollectKStablePromotionDecisionTest(unittest.TestCase):
    def test_decision_defers_stable_promotion_and_keeps_experimental(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("DEFER STABLE PROMOTION", text)
        self.assertIn("Keep `COLLECT_K_BOUNDED` experimental", text)
        self.assertIn("documented_experimental_candidate_with_representative_rtx_reproducibility_evidence", text)
        self.assertIn("standing stable primitive target still excludes `COLLECT_K_BOUNDED`", text)
        self.assertIn("diagnostic,\n   gated-candidate, and environment-flagged optimization paths", text)

    def test_decision_references_required_evidence_chain(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        required = (
            "goal1614_v1_6_4_collect_k_bounds_stress_2026-05-09.md",
            "goal1615_v1_6_4_collect_k_reduced_copy_benchmark_2026-05-09.md",
            "goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_2026-05-09.md",
            "goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09_report.md",
            "goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_2026-05-09.md",
        )
        for artifact in required:
            with self.subTest(artifact=artifact):
                self.assertIn(artifact, text)

    def test_decision_blocks_all_public_claims_and_release_actions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("not public speedup evidence", text)
        self.assertIn("not true zero-copy evidence", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED`\npromotion", text)
        self.assertIn("release tags, or release action", text)

    def test_external_reviews_and_consensus_accept_deferral_only(self) -> None:
        review_paths = (
            ROOT / "docs/reviews/goal1624_v1_6_4_collect_k_stable_promotion_decision_claude_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1624_v1_6_4_collect_k_stable_promotion_decision_gemini_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1624_v1_6_4_collect_k_stable_promotion_decision_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPT", text.upper())
                self.assertIn("COLLECT_K_BOUNDED", text)

        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("deferral decision, not a promotion", consensus)
        self.assertIn("Future stable promotion requires a new decision package", consensus)


if __name__ == "__main__":
    unittest.main()
