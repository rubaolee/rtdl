from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "src" / "rtdsl" / "v2_5_execution_path_policy.py"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2843_v2_5_execution_path_policy_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2844_goal2843_execution_path_policy_consensus_2026-05-31.md"


class Goal2843V25ExecutionPathPolicyTest(unittest.TestCase):
    def test_policy_validates_and_keeps_claims_blocked(self) -> None:
        validation = rt.validate_v2_5_execution_path_policy()

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["policy_version"], rt.V2_5_EXECUTION_PATH_POLICY_VERSION)
        self.assertEqual(validation["operation"], "fixed_radius_ranked_summary_aggregate_3d")

    def test_direct_graph_is_recommended_without_partner_continuation(self) -> None:
        plan = rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=False
        )

        self.assertEqual(plan["selected_path"], "direct_native_graph_replay")
        self.assertEqual(
            plan["recommended_result_mode"],
            rt.V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE,
        )
        self.assertTrue(plan["direct_native_graph_preferred_when_no_partner_continuation"])
        self.assertFalse(plan["same_stream_required_for_partner_continuation"])
        self.assertGreater(plan["same_stream_over_direct_median_ratio"], 1.9)
        self.assertFalse(plan["hidden_auto_dispatch_allowed"])
        self.assertFalse(plan["public_speedup_claim_authorized"])
        self.assertIn("No partner continuation is required", " ".join(plan["reasons"]))

    def test_same_stream_is_recommended_only_when_partner_continuation_is_required(self) -> None:
        plan = rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=True
        )

        self.assertEqual(plan["selected_path"], "same_stream_partner_continuation")
        self.assertEqual(
            plan["recommended_result_mode"],
            rt.V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE,
        )
        self.assertFalse(plan["direct_native_graph_preferred_when_no_partner_continuation"])
        self.assertTrue(plan["same_stream_required_for_partner_continuation"])
        self.assertFalse(plan["auto_select_same_stream_for_speed_allowed"])
        self.assertFalse(plan["true_zero_copy_claim_authorized"])
        self.assertIn("traceable but slower", " ".join(plan["reasons"]))

    def test_non_optix_backend_fails_to_backend_specific_guidance(self) -> None:
        plan = rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=False,
            backend="embree",
        )

        self.assertEqual(plan["selected_path"], "no_optix_graph_policy")
        self.assertEqual(plan["recommended_result_mode"], "backend_specific_policy_required")
        self.assertIn("OptiX fixed-radius graph path", " ".join(plan["reasons"]))

    def test_runner_attaches_execution_path_plan_to_graph_modes(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")

        self.assertIn("plan_v2_5_fixed_radius_aggregate_execution_path", source)
        self.assertIn('"execution_path_plan": execution_path_plan', source)
        self.assertIn('"execution_path_policy_version"', source)

    def test_symbols_are_importable_but_not_public_star_exports(self) -> None:
        for name in (
            "plan_v2_5_fixed_radius_aggregate_execution_path",
            "validate_v2_5_execution_path_policy",
            "V2_5_EXECUTION_PATH_POLICY_VERSION",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)

    def test_report_review_and_consensus_record_goal2841_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2843", report)
        self.assertIn("Goal2841", report)
        self.assertIn("direct native graph replay", report)
        self.assertIn("same-stream only when partner continuation is required", report)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("hidden dispatches", review)
        self.assertIn("slower", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2843 with boundary", consensus)
        self.assertIn("Direct graph without partner continuation | accept", consensus)
        self.assertIn("Public performance/release claims | not authorized", consensus)


if __name__ == "__main__":
    unittest.main()
