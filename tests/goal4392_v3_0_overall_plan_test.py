from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md"
HANDOFF = ROOT / "docs/handoff/HANDOFF_3AI_GOAL4392_V3_0_OVERALL_PLAN_2026-06-15.md"
CLAUDE = ROOT / "docs/reviews/goal4392_claude_review_v3_0_overall_plan_2026-06-15.md"
GEMINI = ROOT / "docs/reviews/goal4392_gemini_review_v3_0_overall_plan_2026-06-15.md"
CONSENSUS = ROOT / "docs/reports/goal4392_3ai_consensus_v3_0_overall_plan_2026-06-15.md"


class Goal4392V30OverallPlanTest(unittest.TestCase):
    def test_plan_records_current_state_and_blocks_implementation(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        self.assertIn("v3_0_m1_design_allowed_implementation_blocked", text)
        self.assertIn("This document does not authorize V3.0 implementation", text)
        self.assertIn("native fused implementation", text)
        self.assertIn("planner implementation", text)
        self.assertIn("public performance claims", text)

    def test_plan_includes_all_goal4384_binding_conditions(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        required = [
            "v2.14 closeout is a hard precondition",
            "frozen execution-graph IR design document before M2 code starts",
            "forbid app-specific names in the public Python API surface",
            "RTDBSCAN fused-continuation pilot must prove cross-app reuse",
            "Same-stream partner claims need hardware-observable evidence",
            "No V3.0 public performance claim is authorized",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

    def test_public_api_boundary_is_app_agnostic(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        self.assertIn("GraphValue", text)
        self.assertIn("PreparedGraph", text)
        self.assertIn("PartnerNode", text)
        self.assertIn("No native RayJoin engine", text)
        self.assertIn("No native DBSCAN engine", text)
        self.assertIn("No native Barnes-Hut force-law engine", text)
        self.assertIn("No native contact-manifold physics engine", text)
        self.assertIn("raw arbitrary OptiX callback functions as the stable RTDL user API", text)

    def test_partner_policy_requires_best_partner_and_numba_reference(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        self.assertIn("test the best practical partner implementation", text)
        self.assertIn("also test a Numba reference", text)
        self.assertIn("if the Numba reference is omitted", text)
        self.assertIn("disclose every partner in performance tables", text)
        self.assertIn("CUDA events or Nsight-level evidence", text)
        self.assertIn("pointer identity, residency, lifetime, and transfer evidence", text)

    def test_milestones_are_ordered_and_claims_wait_until_release_harness(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        for milestone in ("M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7"):
            self.assertIn(f"| {milestone} |", text)
        self.assertIn("external Claude/Gemini review passed", text)
        self.assertIn("M3-grade phase accounting", text)
        self.assertIn("Implementation may not proceed past M1 until M1 is frozen and reviewed", text)
        self.assertIn("Public V3.0 performance claims may not proceed until M7", text)
        self.assertIn("Goal4384 used M5 as the release-grade public-claim gate", text)

    def test_benchmark_targets_cover_v3_critical_apps(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        for workload in (
            "RTDBSCAN",
            "RayJoin LSI/PIP/overlay",
            "Barnes-Hut",
            "Contact and robot collision",
            "RayDB and graph/ranked-summary workloads",
            "Triangle and distance-like apps",
        ):
            self.assertIn(workload, text)
        self.assertIn("same paper contract and dataset timing basis", text)

    def test_handoff_requests_three_ai_gate_review(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        self.assertIn("Goal4392 V3.0 Overall Plan Review Handoff", text)
        self.assertIn("VERDICT: ACCEPT", text)
        self.assertIn("VERDICT: ACCEPT_WITH_NOTES", text)
        self.assertIn("VERDICT: REQUEST_CHANGES", text)
        self.assertIn("REQUEST_CHANGES blocks V3.0 from proceeding", text)
        self.assertIn("best practical partner plus Numba reference", text)

    def test_consensus_records_acceptable_external_reviews_when_present(self) -> None:
        if not CONSENSUS.exists():
            self.skipTest("consensus file is created after external review")
        text = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("v3_0_overall_plan_accepted_m1_design_only_implementation_blocked", text)
        self.assertIn("Claude", text)
        self.assertIn("Gemini", text)
        self.assertNotIn("VERDICT: REQUEST_CHANGES", text)

        for review_path in (CLAUDE, GEMINI):
            review = review_path.read_text(encoding="utf-8")
            match = re.search(r"^VERDICT: (ACCEPT|ACCEPT_WITH_NOTES|REQUEST_CHANGES)$", review, re.MULTILINE)
            self.assertIsNotNone(match, f"{review_path} must include an exact verdict line")
            self.assertNotEqual("REQUEST_CHANGES", match.group(1))


if __name__ == "__main__":
    unittest.main()
