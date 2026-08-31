from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_hit_columns
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_payload_columns


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2980_neutral_seam_scope_out_closeout_decision_2026-06-01.md"


class Goal2980NeutralSeamScopeOutCloseoutDecisionTest(unittest.TestCase):
    def test_closeout_decision_scopes_out_full_composition(self) -> None:
        decision = rt.v2_5_neutral_seam_closeout_decision()
        validation = rt.validate_v2_5_neutral_seam_closeout_decision(decision)

        self.assertEqual("accept", validation["status"])
        self.assertEqual("C-3b_scope_out_for_v2_5", decision["selected_option"])
        self.assertTrue(decision["multi_partner_composition_scaffolded"])
        self.assertFalse(decision["multi_partner_composition_delivered"])
        self.assertFalse(decision["full_partner_neutral_handoff_delivered"])
        self.assertFalse(decision["composition_claim_authorized"])
        self.assertFalse(decision["true_zero_copy_authorized"])
        self.assertFalse(decision["automatic_triton_selection_allowed"])
        self.assertEqual(("triton",), decision["torch_carrier_allowed_only_for_partners"])
        self.assertEqual("cuda_array_interface_descriptor", decision["non_triton_device_carrier_protocol"])
        self.assertIn(
            "end_to_end_partner_neutral_device_resident_composition",
            decision["v2_5_not_delivered"],
        )
        self.assertIn(
            "whole_app_residency_measurement_on_at_least_one_app",
            decision["deferred_to_v3_0_or_later"],
        )

    def test_existing_transfer_plans_match_scope_out_boundary(self) -> None:
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

        self.assertEqual("cuda_array_interface_to_torch_carrier", triton["carrier_protocol"])
        self.assertTrue(triton["torch_carrier_allowed"])
        for plan in (cupy, numba):
            self.assertEqual("cuda_array_interface_descriptor", plan["carrier_protocol"])
            self.assertFalse(plan["torch_carrier_allowed"])
            self.assertFalse(plan["torch_is_neutral_protocol"])
            self.assertFalse(plan["silent_cross_partner_torch_coercion_allowed"])

    def test_readiness_and_report_record_no_release_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        for phrase in (
            "Goal2980",
            "scopes out full partner-neutral composition",
            "Torch is not a neutral protocol",
            "Not delivered in v2.5",
            "not a release authorization",
        ):
            self.assertIn(phrase, text)
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2980_neutral_seam_scope_out_closeout_decision_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2980_neutral_seam_scope_out_closeout_decision_green", packet["allowed_next_actions"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertEqual("accept", rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)["status"])

    def test_symbols_are_importable_but_not_star_exports(self) -> None:
        self.assertTrue(hasattr(rt, "v2_5_neutral_seam_closeout_decision"))
        self.assertTrue(hasattr(rt, "validate_v2_5_neutral_seam_closeout_decision"))
        self.assertNotIn("v2_5_neutral_seam_closeout_decision", rt.__all__)
        self.assertNotIn("validate_v2_5_neutral_seam_closeout_decision", rt.__all__)


if __name__ == "__main__":
    unittest.main()
