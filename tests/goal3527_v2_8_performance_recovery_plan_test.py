from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3527_v2_8_performance_recovery_and_promoted_path_plan_2026-06-05.md"
CLAUDE_HANDOFF = (
    ROOT
    / "docs"
    / "handoff"
    / "HANDOFF_CLAUDE_GOAL3527_V2_8_PERFORMANCE_RECOVERY_PLAN_REVIEW_2026-06-05.md"
)
GEMINI_HANDOFF = (
    ROOT
    / "docs"
    / "handoff"
    / "HANDOFF_GEMINI_GOAL3527_V2_8_PERFORMANCE_RECOVERY_PLAN_REVIEW_2026-06-05.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal3528_claude_review_goal3527_v2_8_performance_recovery_plan_2026-06-05.md"
)
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal3529_gemini_review_goal3527_v2_8_performance_recovery_plan_2026-06-05.md"
)
CONSENSUS = ROOT / "docs" / "reports" / "goal3527_v2_8_performance_recovery_plan_3ai_consensus_2026-06-05.md"


class Goal3527V28PerformanceRecoveryPlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.report = REPORT.read_text(encoding="utf-8")
        self.lowered = self.report.lower()

    def test_plan_names_user_problem_and_goal3524_diagnostic_boundary(self) -> None:
        self.assertIn("Goal3524", self.report)
        self.assertIn("same-runner diagnostic table", self.report)
        self.assertIn("not the final promoted-v2.8 table", self.report)
        self.assertIn("0.401x", self.report)
        self.assertIn("1.096x", self.report)

    def test_plan_requires_two_tables_and_promoted_path_evidence(self) -> None:
        self.assertIn("promoted-path performance table", self.lowered)
        self.assertIn("same-runner diagnostic", self.lowered)
        self.assertIn("evolved-contract", self.report)
        self.assertIn("must not collapse evolved app contracts into fake ratios", self.lowered)
        self.assertIn("sub_millisecond_measurement_guard", self.report)
        self.assertIn("median-of-N", self.report)
        self.assertIn("launch-overhead dominated", self.report)
        self.assertIn("must not be used as a positive speedup headline", self.lowered)

    def test_weak_row_priorities_are_explicit(self) -> None:
        required = (
            "barnes_hut_optix_node_coverage",
            "spatial_rayjoin_optix_prepared_full_route",
            "rt_dbscan_optix_grouped_stream",
            "rtnn_optix_prepared_3d_ranked_summary",
            "librts_optix_aabb_index",
            "triangle_counting_optix_rt_graph_2a1_partner",
            "robot_collision_optix_prepared_device_buffers",
            "raydb_optix_partner_resident_count",
            "contact_manifold_optix_aabb_broadphase_collect_k",
        )
        for case_id in required:
            self.assertIn(case_id, self.report)
        self.assertIn("P0", self.report)
        self.assertIn("recover to at least parity", self.lowered)
        self.assertIn("0.95x", self.report)
        self.assertIn("honest_regression", self.report)

    def test_rayjoin_promoted_contract_preflight_is_required(self) -> None:
        self.assertIn("Before the RayJoin promoted-path rows are measured", self.report)
        self.assertIn("count/parity", self.report)
        self.assertIn("relation columns", self.report)
        self.assertIn("shape-pair payload", self.report)
        self.assertIn("overlay-area continuation", self.report)
        self.assertIn("must be sequenced as implementation work before measurement", self.report)

    def test_app_agnostic_and_partner_boundaries_are_preserved(self) -> None:
        self.assertIn("no app-specific native-engine shortcuts", self.lowered)
        self.assertIn("app developer does not write OptiX code", self.report)
        self.assertIn("CuPy", self.report)
        self.assertIn("PyTorch must not silently enter", self.report)
        self.assertIn("partners remain explicit", self.lowered)

    def test_no_public_or_release_claim_is_authorized(self) -> None:
        self.assertIn("No public speedup wording", self.report)
        self.assertIn("No implementation should start until Codex, Claude, and Gemini agree", self.report)
        self.assertIn("Sub-millisecond promoted-path rows", self.report)
        self.assertIn("RayJoin promoted contracts must be confirmed runnable", self.report)
        forbidden = (
            "public speedup claim authorized",
            "release authorized",
            "true zero-copy claim authorized",
            "whole-app speedup claim authorized",
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, self.lowered)

    def test_handoffs_request_distinct_external_reviews(self) -> None:
        claude = CLAUDE_HANDOFF.read_text(encoding="utf-8")
        gemini = GEMINI_HANDOFF.read_text(encoding="utf-8")
        self.assertIn("goal3528_claude_review", claude)
        self.assertIn("goal3529_gemini_review", gemini)
        self.assertIn("Barnes-Hut P0", claude)
        self.assertIn("promoted-v2.8", gemini)
        for text in (claude, gemini):
            self.assertIn("accept-with-boundary", text)
            self.assertIn("Do not edit files other than the requested", text)

    def test_external_reviews_and_consensus_accept_amended_plan(self) -> None:
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", claude)
        self.assertIn("sub-millisecond scale", claude)
        self.assertIn("Promoted-path contracts for RayJoin are not confirmed", claude)
        self.assertIn("`accept`", gemini)
        self.assertIn("Claude Boundary Incorporated", consensus)
        self.assertIn("Sub-millisecond measurement guard", consensus)
        self.assertIn("RayJoin promoted-contract preflight", consensus)
        self.assertIn("0.95x", consensus)
        self.assertIn("not a v2.8 release authorization", consensus)


if __name__ == "__main__":
    unittest.main()
