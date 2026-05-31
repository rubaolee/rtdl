from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_hit_columns
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_payload_columns


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2775_hit_stream_neutral_seam_reconciliation_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2775_gemini_review_hit_stream_neutral_seam_reconciliation_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2775_hit_stream_neutral_seam_reconciliation_consensus_2026-05-31.md"


class Goal2775HitStreamNeutralSeamReconciliationTest(unittest.TestCase):
    def test_reconciliation_contract_makes_neutral_seam_authoritative(self) -> None:
        contract = rt.describe_v2_5_hit_stream_neutral_seam_reconciliation()

        self.assertEqual(
            contract["contract_version"],
            rt.GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        )
        self.assertEqual(
            contract["neutral_buffer_seam_contract_version"],
            rt.V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        )
        self.assertTrue(contract["support_matrix_is_authority"])
        self.assertFalse(contract["torch_is_neutral_protocol"])
        self.assertFalse(contract["torch_is_partner"])
        self.assertEqual(contract["torch_carrier_allowed_only_for_partners"], ("triton",))
        self.assertEqual(contract["non_triton_device_carrier_protocol"], "cuda_array_interface_descriptor")
        self.assertFalse(contract["silent_cross_partner_torch_coercion_allowed"])
        self.assertIn("bounded_triton_launch_carrier", contract["legacy_torch_helper_status"])
        self.assertIn("must not become a hidden neutral protocol", contract["claim_boundary"])

    def test_torch_carrier_adapter_is_labeled_as_triton_only_under_neutral_seam(self) -> None:
        adapter = rt.describe_v2_5_hit_stream_torch_carrier_adapter(
            _device_hit_columns(),
            _device_payload_columns(),
        )

        self.assertEqual(
            adapter["neutral_seam_reconciliation_version"],
            rt.GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        )
        self.assertEqual(
            adapter["neutral_buffer_seam_contract_version"],
            rt.V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        )
        self.assertTrue(adapter["support_matrix_is_authority"])
        self.assertFalse(adapter["torch_is_neutral_protocol"])
        self.assertEqual(adapter["torch_carrier_allowed_only_for_partner"], "triton")
        self.assertFalse(adapter["silent_cross_partner_torch_coercion_allowed"])
        self.assertFalse(adapter["true_zero_copy_authorized"])
        self.assertFalse(adapter["public_speedup_claim_authorized"])

    def test_transfer_plans_do_not_use_torch_carrier_for_non_triton_partners(self) -> None:
        triton = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_sum_f64",
            partner="triton",
        )
        cupy = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="hit_stream_grouped_ray_id_primitive_i64",
            partner="cupy",
        )
        numba = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_count_i64",
            partner="numba",
        )

        self.assertEqual(triton["carrier_protocol"], "cuda_array_interface_to_torch_carrier")
        self.assertTrue(triton["torch_carrier_allowed"])
        self.assertFalse(triton["torch_is_neutral_protocol"])
        self.assertTrue(triton["support_matrix_is_authority"])

        for plan in (cupy, numba):
            with self.subTest(partner=plan["selected_partner"]):
                self.assertEqual(plan["carrier_protocol"], "cuda_array_interface_descriptor")
                self.assertFalse(plan["torch_carrier_allowed"])
                self.assertFalse(plan["torch_is_neutral_protocol"])
                self.assertFalse(plan["silent_cross_partner_torch_coercion_allowed"])
                self.assertTrue(plan["support_matrix_is_authority"])

    def test_continuation_plan_carries_reconciliation_metadata(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_continuation(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="hit_stream_grouped_ray_id_primitive_i64",
            partner="cupy",
        )

        self.assertEqual(
            plan["neutral_seam_reconciliation_version"],
            rt.GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        )
        self.assertEqual(
            plan["partner_transfer_plan"]["neutral_seam_reconciliation_version"],
            rt.GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        )
        self.assertEqual(plan["selected_partner"], rt.V2_5_CONFORMANCE_PARTNER)
        self.assertFalse(plan["fail_closed"])
        self.assertTrue(plan["execution_allowed_without_copy"])
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_report_records_goal2775_boundary(self) -> None:
        report = REPORT.read_text()
        review = REVIEW.read_text()
        consensus = CONSENSUS.read_text()

        self.assertIn("neutral buffer seam is the authority", report)
        self.assertIn("Torch remains only a Triton launch carrier", report)
        self.assertIn("no public speedup", report)
        self.assertIn("no true zero-copy", report)
        self.assertIn("**accept.**", review)
        self.assertIn("`accept`", consensus)


if __name__ == "__main__":
    unittest.main()
