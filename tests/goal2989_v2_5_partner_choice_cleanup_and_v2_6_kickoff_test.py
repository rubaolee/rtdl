from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2989_v2_5_partner_choice_cleanup_and_v2_6_kickoff_2026-06-01.md"
)
CLAUDE_V2_6 = (
    ROOT
    / "docs"
    / "reports"
    / "claude_v2_6_numba_first_class_partner_work_for_main_ai_2026-05-31.md"
)


class Goal2989PartnerChoiceCleanupAndV26KickoffTest(unittest.TestCase):
    def test_v2_5_doctrine_records_user_choice_and_paused_triton(self) -> None:
        doctrine = rt.v2_5_primitive_first_selection_doctrine()
        validation = rt.validate_v2_5_primitive_first_selection_doctrine(doctrine)

        self.assertEqual("accept", validation["status"])
        self.assertIn("user_selects_partner_explicitly", doctrine["partner_choice_rule"])
        self.assertIn("same_contract", doctrine["partner_choice_rule"])
        self.assertIn("partner_choice_belongs_to_the_user", doctrine["partner_authority_rule"])
        self.assertIn("high_performance_support", doctrine["supported_partner_duty"])
        self.assertIn("reference_or_recommended", doctrine["benchmark_app_role"])
        self.assertIn("app_agnostic", doctrine["generic_engine_rule"])
        self.assertIn("paused", doctrine["triton_role"])
        self.assertFalse(doctrine["automatic_partner_selection_allowed"])
        self.assertFalse(doctrine["automatic_triton_selection_allowed"])
        self.assertFalse(doctrine["release_readiness_authorized"])

    def test_partner_choice_cleanup_policy_is_fail_closed(self) -> None:
        policy = rt.v2_5_partner_choice_cleanup_policy()
        validation = rt.validate_v2_5_partner_choice_cleanup_policy(policy)
        guidance = rt.v2_5_partner_selection_guidance()

        self.assertEqual("accept", validation["status"])
        self.assertEqual(rt.V2_5_PARTNER_CHOICE_CLEANUP_VERSION, policy["cleanup_version"])
        self.assertTrue(policy["user_partner_choice_authority"])
        self.assertIn("reference_or_recommended", policy["benchmark_app_role"])
        self.assertIn("app_agnostic", policy["generic_engine_boundary"])
        self.assertIn("ignored", policy["triton_recommended_path_status"])
        self.assertEqual(policy["cleanup_version"], guidance["partner_choice_cleanup_version"])
        self.assertTrue(guidance["user_partner_choice_authority"])
        self.assertFalse(policy["automatic_partner_selection_allowed"])
        self.assertFalse(policy["release_readiness_authorized"])

    def test_v2_6_roadmap_starts_with_neutral_seam_and_numba(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(roadmap, repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(rt.V2_6_ROADMAP_VERSION, roadmap["roadmap_version"])
        self.assertIn("neutral_buffer_seam", roadmap["opening_goal"])
        self.assertIn("numba", roadmap["primary_partner_track"])
        self.assertIn("users_choose", roadmap["partner_choice_rule"])
        self.assertIn("high_performance_support", roadmap["supported_partner_duty"])
        self.assertIn("reference_or_recommended", roadmap["benchmark_app_role"])
        self.assertIn("app_agnostic", roadmap["generic_engine_boundary"])
        self.assertIn("ignored", roadmap["triton_status"])
        self.assertEqual(
            ("N-0", "N-1", "N-2", "N-3", "N-4"),
            tuple(step["step"] for step in roadmap["sequenced_work"]),
        )
        self.assertTrue(roadmap["minimum_demonstration"]["cpu_reference_parity_required"])
        self.assertTrue(roadmap["minimum_demonstration"]["same_contract_perf_gate_required_before_speedup_claim"])
        self.assertFalse(roadmap["automatic_partner_selection_allowed"])
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])
        self.assertFalse(roadmap["release_authorized"])

    def test_readiness_indexes_cleanup_and_allows_v2_6_start_without_release(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2989_v2_5_partner_choice_cleanup_and_v2_6_kickoff_2026-06-01.md"
            ]
        )
        self.assertEqual("accept", packet["core_validations"]["partner_choice_cleanup_policy"]["status"])
        self.assertEqual("accept", packet["core_validations"]["v2_6_roadmap"]["status"])
        self.assertIn(
            "begin_v2_6_neutral_seam_numba_partner_lane_after_goal2989",
            packet["allowed_next_actions"],
        )
        self.assertEqual("accept", validation["status"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertIn("v2_5_release", packet["blocked_actions"])

    def test_docs_capture_user_decisions_and_claude_reference(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        claude = CLAUDE_V2_6.read_text(encoding="utf-8")

        for phrase in (
            "Users choose supported partners",
            "Benchmark apps provide reference or recommended implementations",
            "generic app-agnostic primitive engine",
            "Triton is paused/ignored",
            "v2.6 begins",
            "Numba first-class",
            "does not authorize",
        ):
            self.assertIn(phrase, report)
        self.assertIn("Numba as a First-Class Partner", claude)
        self.assertIn("partner choice belongs to the user", claude)


if __name__ == "__main__":
    unittest.main()
