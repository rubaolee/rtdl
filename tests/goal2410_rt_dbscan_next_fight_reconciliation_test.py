from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal2409_claude_review_goal2408_rt_dbscan_next_fight_plan_2026-05-19.md"
RECONCILIATION = ROOT / "docs" / "reports" / "goal2410_codex_claude_rt_dbscan_next_fight_reconciliation_2026-05-19.md"


class Goal2410RtDbscanNextFightReconciliationTest(unittest.TestCase):
    def test_claude_review_accepts_candidate_b_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Verdict: **accept-with-boundary**", review)
        self.assertIn("Candidate B is the right next fight", review)
        self.assertIn("Raw any-hit atomic union should not be revisited", review)
        self.assertIn("mixed-core", review.lower())
        self.assertIn("fast_path_active", review)

    def test_reconciliation_records_the_selected_goal2409_contract(self) -> None:
        report = RECONCILIATION.read_text(encoding="utf-8")

        self.assertIn("planning round closed", report)
        self.assertIn("radius_graph_components_3d_cupy_cell_graph_partner_columns", report)
        self.assertIn("optix_rt_core_flags_cupy_cell_graph_components_3d", report)
        self.assertIn("cell_graph_fast_path_active", report)
        self.assertIn("fallback_adapter", report)

    def test_reconciliation_keeps_boundary_and_pass_fail_policy(self) -> None:
        report = RECONCILIATION.read_text(encoding="utf-8")

        self.assertIn("No DBSCAN-native ABI", report)
        self.assertIn("no broad RT-core or release claim is authorized", report)
        self.assertIn("mixed-core fallback is observed and correct", report)
        self.assertIn("dense all-core fast path never activates", report)
        self.assertIn("does not authorize release closure", report)


if __name__ == "__main__":
    unittest.main()
