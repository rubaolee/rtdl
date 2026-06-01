from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2978_primitive_first_v2_5_closeout_policy_2026-06-01.md"
CURRENT_ARCH = ROOT / "docs" / "current_architecture.md"
CURRENT_SUPPORT = ROOT / "docs" / "current_main_support_matrix.md"
PARTNER_BOUNDARY = ROOT / "docs" / "partner_acceleration_boundaries.md"


class Goal2978PrimitiveFirstV25CloseoutPolicyTest(unittest.TestCase):
    def test_doctrine_validates_and_blocks_overclaims(self) -> None:
        doctrine = rt.v2_5_primitive_first_selection_doctrine()
        validation = rt.validate_v2_5_primitive_first_selection_doctrine(doctrine)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(
            doctrine["doctrine_version"],
            rt.V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION,
        )
        self.assertIn("primitive_first", doctrine["fast_path_rule"])
        self.assertIn("unfused", doctrine["partner_use_rule"])
        self.assertIn("same_contract", doctrine["partner_choice_rule"])
        self.assertIn("no fused native primitive", doctrine["tier_b_definition"])
        self.assertFalse(doctrine["automatic_triton_selection_allowed"])
        self.assertFalse(doctrine["triton_default_allowed"])
        self.assertFalse(doctrine["preview_kernel_availability_implies_selection"])
        self.assertFalse(doctrine["release_readiness_authorized"])

    def test_execution_path_policy_indexes_doctrine(self) -> None:
        validation = rt.validate_v2_5_execution_path_policy()
        direct = rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=False
        )
        continuation = rt.plan_v2_5_fixed_radius_aggregate_execution_path(
            requires_partner_continuation=True
        )

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(
            validation["primitive_first_selection_doctrine_version"],
            rt.V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION,
        )
        self.assertTrue(direct["primitive_first_native_when_no_partner_continuation"])
        self.assertFalse(direct["automatic_triton_selection_allowed"])
        self.assertTrue(continuation["partner_continuation_reserved_for_required_continuation"])
        self.assertFalse(continuation["automatic_triton_selection_allowed"])

    def test_partner_guidance_and_tier_map_carry_closeout_rule(self) -> None:
        guidance = rt.v2_5_partner_selection_guidance()
        manifest = rt.v2_5_tiered_benchmark_manifest()
        migration = rt.v2_5_triton_benchmark_app_migration_plan()

        self.assertEqual(rt.validate_v2_5_partner_selection_guidance(guidance, repo_root=ROOT)["status"], "accept")
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")
        self.assertEqual(rt.validate_v2_5_triton_benchmark_app_migration_plan()["status"], "accept")

        self.assertEqual(
            guidance["primitive_first_selection_doctrine_version"],
            rt.V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION,
        )
        self.assertIn("primitive_first", guidance["fast_path_rule"])
        self.assertIn("unfused", guidance["partner_use_rule"])
        self.assertFalse(guidance["automatic_triton_selection_allowed"])

        self.assertEqual(
            manifest["primitive_first_selection_doctrine_version"],
            rt.V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION,
        )
        self.assertIn("no fused native primitive", manifest["tier_b_definition"])
        self.assertFalse(manifest["automatic_triton_selection_allowed"])

        self.assertTrue(migration["closeout_selection_doctrine_integrated"])
        self.assertIn("primitive_first", migration["fast_path_rule"])
        self.assertIn("unfused", migration["partner_use_rule"])
        self.assertFalse(migration["triton_default_allowed"])

    def test_current_docs_no_longer_present_triton_as_default_direction(self) -> None:
        arch = CURRENT_ARCH.read_text(encoding="utf-8")
        support = CURRENT_SUPPORT.read_text(encoding="utf-8")
        boundary = PARTNER_BOUNDARY.read_text(encoding="utf-8")
        arch_normalized = " ".join(arch.lower().split())

        self.assertNotIn("direction is Triton-first", arch)
        self.assertNotIn("Triton primary. Numba fallback", arch)
        self.assertIn("active v2.5 closeout rule is now primitive-first", arch_normalized)
        self.assertIn("never auto-select Triton", arch)

        self.assertNotIn("Active partner direction: v2.5 Triton-first", support)
        self.assertIn("Active v2.5 closeout direction", support)
        self.assertIn("partner chosen by same-contract evidence", support)

        self.assertIn("Post-Goal2978 closeout correction", boundary)
        self.assertIn("supersedes that wording for new work", boundary)
        self.assertIn("never auto-select Triton", boundary)

    def test_report_records_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2978", text)
        self.assertIn("primitive-first native RTDL is the fast path", text)
        self.assertIn("Tier B is a coverage/unfused-continuation category", text)
        self.assertIn("not release-authorizing", text)
        self.assertIn("Goal2977 second-architecture packet gap", text)

    def test_symbols_are_importable_but_not_star_exports(self) -> None:
        for name in (
            "V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION",
            "v2_5_primitive_first_selection_doctrine",
            "validate_v2_5_primitive_first_selection_doctrine",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)


if __name__ == "__main__":
    unittest.main()
