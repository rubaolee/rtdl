from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3482_overlay_area_pre_kernel_policy_2026-06-05.md"


class Goal3482OverlayAreaPreKernelPolicyTest(unittest.TestCase):
    def test_pre_kernel_policy_validates(self) -> None:
        policy = rt.describe_v2_8_overlay_area_pre_kernel_policy()
        validation = rt.validate_v2_8_overlay_area_pre_kernel_policy()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(policy["target"], "scalar_exact_area")
        self.assertEqual(policy["topology_input_status"], "requires_prepared_simple_polygon_component_payload")
        self.assertEqual(policy["unsupported_topology_status"], "unsupported_topology_not_canonicalized")
        self.assertEqual(
            policy["scratch_policy"],
            "tile_triangle_pairs_fail_closed_on_tile_or_accumulator_overflow",
        )
        self.assertEqual(policy["oracle_strict_positive_row_count"], 1090)
        self.assertEqual(policy["oracle_positive_row_count"], 1086)
        self.assertEqual(policy["oracle_positive_row_threshold"], 1.0e-10)
        self.assertAlmostEqual(policy["effective_total_tolerance"], max(1.0e-8, 1.0e-9 * 26.08321766231042))

    def test_policy_blocks_claims(self) -> None:
        policy = rt.describe_v2_8_overlay_area_pre_kernel_policy()

        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "full_overlay_completion_claim_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(policy[field])

    def test_report_records_claude_risk_order(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "explicit tolerance",
            "requires_prepared_simple_polygon_component_payload",
            "unsupported_topology_not_canonicalized",
            "bounded tiles",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
