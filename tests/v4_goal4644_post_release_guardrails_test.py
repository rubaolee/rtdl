from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_goal4642_final_authorization_packet import validate_v4_goal4642_final_authorization_packet
from rtdsl.v4_goal4644_post_release_guardrails import V4_GOAL4644_DECISION
from rtdsl.v4_goal4644_post_release_guardrails import validate_v4_goal4644_post_release_guardrails
from rtdsl.v4_release_decision import v4_goal4632_release_decision


PUBLIC_FRONT_DOOR_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "current_v4_status.md",
    ROOT / "docs" / "learn" / "performance_wording.md",
    ROOT / "future" / "v4" / "tier2_operator_catalog.md",
    ROOT / "future" / "v4" / "v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md",
)
GOAL4644_DOC = ROOT / "future" / "v4" / "v4_goal4644_post_release_guardrails_2026-06-25.md"
COMPLETION_AUDIT = ROOT / "future" / "v4" / "v4_goal4633_4644_completion_audit_2026-06-25.md"


class V4Goal4644PostReleaseGuardrailsTest(unittest.TestCase):
    def test_goal4644_machine_record_exists_and_tracks_current_goal4742_boundary(self) -> None:
        decision = validate_v4_goal4644_post_release_guardrails(ROOT)

        self.assertEqual(V4_GOAL4644_DECISION, decision["decision"])
        self.assertEqual("v4_python_edsl_release_candidate_guardrails_active_goal4744", decision["status"])
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["formal_release_authorized"])
        self.assertTrue(decision["bounded_operator_surface_available"])
        self.assertFalse(decision["app_level_high_performance_authorized"])
        self.assertTrue(decision["v4_python_edsl_release_candidate_supported"])
        self.assertTrue(decision["operator_pushdown_workflow_high_performance_supported"])
        self.assertFalse(decision["legacy_all_app_high_performance_supported"])
        self.assertEqual(
            "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim",
            decision["current_app_level_decision_label"],
        )
        self.assertFalse(decision["release_scope_reopened"])
        self.assertEqual(10, decision["measured_surfaces_count"])
        self.assertEqual(0, decision["candidate_surfaces_count"])
        self.assertEqual(6, decision["review_cadence_hours"])
        self.assertEqual(24, decision["three_ai_consensus_cadence_hours"])
        self.assertEqual(
            "claude_accept_goal4644_post_release_guardrails_no_amendments",
            decision["external_review_status"],
        )

        text = GOAL4644_DOC.read_text(encoding="utf-8")
        self.assertIn("v4_bounded_operator_guardrails_active_goal4655_corrected", text)
        self.assertIn("does not reopen V4 scope", text)
        self.assertIn("formal\napp-level high-performance V4 release wording is not authorized", text)

        audit = COMPLETION_AUDIT.read_text(encoding="utf-8")
        self.assertIn("goal4633_4644_complete_with_goal4644_claude_review", audit)
        self.assertIn("Goal4633-4644 is complete", audit)

    def test_machine_forbidden_claims_cover_deferred_and_reproduction_overclaims(self) -> None:
        release_decision = v4_goal4632_release_decision()
        packet = validate_v4_goal4642_final_authorization_packet(ROOT)
        post_release = validate_v4_goal4644_post_release_guardrails(ROOT)

        required_forbidden = {
            "Barnes-Hut new V4-over-V3 speedup",
            "Spatial RayJoin speedup",
            "LibRTS paper reproduction",
        }
        self.assertTrue(required_forbidden.issubset(set(release_decision["forbidden_claims"])))
        self.assertTrue(required_forbidden.issubset(set(packet["forbidden_claims"])))
        self.assertTrue(required_forbidden.issubset(set(post_release["forbidden_claims"])))

    def test_candidate_surfaces_are_not_counted_as_measured(self) -> None:
        decision = v4_goal4632_release_decision()

        self.assertEqual(10, decision["measured_surfaces_count"])
        self.assertEqual(0, decision["candidate_surfaces_count"])
        self.assertEqual(0, decision["coverage_summary"]["by_status"]["candidate_not_measured_release_coverage"])
        self.assertEqual(2, decision["coverage_summary"]["by_status"]["deferred_or_uncovered_v4_0"])

    def test_public_docs_keep_release_caveats_and_no_stale_goal4640_4641_gate(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Python eDSL/operator-pushdown", readme)
        self.assertIn("complete 10-app RT-core matrix", readme)
        self.assertIn("brute-force partner/CPU baselines", readme)
        self.assertNotIn("gated on public-doc\ncleanup, clean-tree reproducibility", readme)

        required_caveats = (
            "whole-application speedup",
            "public true-zero-copy",
            "Tier-3",
            "CuPy",
        )
        for path in PUBLIC_FRONT_DOOR_DOCS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                for caveat in required_caveats:
                    self.assertIn(caveat, text)

    def test_deferred_families_remain_out_of_v4_0_claims(self) -> None:
        packet = (ROOT / "future" / "v4" / "v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("spatial_rayjoin", packet)
        self.assertIn("barnes_hut", packet)
        self.assertIn("deferred/excluded", packet)
        self.assertIn("must not be used in V4.0 coverage or speedup claims", packet)


if __name__ == "__main__":
    unittest.main()
