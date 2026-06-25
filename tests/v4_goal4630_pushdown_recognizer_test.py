from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl.v4 as rt_v4
import rtdsl.v4_operator_catalog as catalog


class V4Goal4630PushdownRecognizerTest(unittest.TestCase):
    def test_declarative_fixed_radius_request_routes_to_measured_tier2_surface(self) -> None:
        recognition = catalog.recognize_v4_pushdown_request(
            {
                "kind": "itre_relation_reduce",
                "relation": "fixed_radius",
                "reduction": "count_threshold",
            },
            partner="torch",
        )

        self.assertEqual("pushdown_recognized_measured_tier2", recognition.status)
        self.assertTrue(recognition.pushdown_recognized)
        self.assertFalse(recognition.fail_closed)
        self.assertEqual("v4_fixed_radius_count_threshold_2d_device_arrays", recognition.plan.api_surface)
        self.assertEqual("FIXED_RADIUS_COUNT_THRESHOLD_2D", recognition.plan.generic_primitive)
        self.assertTrue(recognition.plan.measured_partner)

    def test_grouped_i64_request_routes_through_frontdoor(self) -> None:
        recognition = rt_v4.recognize_pushdown_request_v4(
            {
                "kind": "itre_grouped_reduce",
                "operator": "primitive_grouped_reduction",
            },
            partner="torch",
        )

        self.assertEqual("pushdown_recognized_measured_tier2", recognition.status)
        self.assertEqual(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            recognition.plan.api_surface,
        )
        self.assertEqual("grouped_i64_reduction", recognition.plan.continuation_class)
        self.assertEqual(catalog.V4_GOAL4630_PUSHDOWN_RECOGNIZER_STATUS, recognition.recognizer_status)

    def test_weighted_sum_is_recognized_as_measured_after_goal4633(self) -> None:
        recognition = catalog.recognize_v4_pushdown_request(
            {
                "kind": "itre_reduce",
                "operator": "ray_triangle_any_hit_weighted_sum",
            },
            partner="torch",
        )

        self.assertEqual("pushdown_recognized_measured_tier2", recognition.status)
        self.assertTrue(recognition.pushdown_recognized)
        self.assertFalse(recognition.fail_closed)
        self.assertEqual("tier2_measured_ready", recognition.plan.status)
        self.assertTrue(recognition.plan.measured_partner)
        self.assertFalse(recognition.measured_catalog_claim_authorized)
        self.assertFalse(recognition.release_claim_authorized)

    def test_unmeasured_partner_fails_closed(self) -> None:
        recognition = catalog.recognize_v4_pushdown_request(
            {
                "operator": "fixed-radius",
            },
            partner="cupy",
        )

        self.assertEqual("pushdown_fail_closed_unmeasured_partner", recognition.status)
        self.assertFalse(recognition.pushdown_recognized)
        self.assertTrue(recognition.fail_closed)
        self.assertEqual("tier2_declared_unmeasured_partner", recognition.plan.status)
        self.assertIsNone(recognition.plan.api_surface)
        self.assertFalse(recognition.cupy_performance_claim_authorized)

    def test_unmeasured_candidate_partner_fails_closed(self) -> None:
        recognition = catalog.recognize_v4_pushdown_request(
            {
                "operator": "ray_triangle_any_hit_weighted_sum",
            },
            partner="cupy",
        )

        self.assertEqual("pushdown_fail_closed_unmeasured_partner", recognition.status)
        self.assertFalse(recognition.pushdown_recognized)
        self.assertTrue(recognition.fail_closed)
        self.assertEqual("tier2_declared_unmeasured_partner", recognition.plan.status)
        self.assertIsNone(recognition.plan.api_surface)
        self.assertFalse(recognition.plan.measured_partner)
        self.assertFalse(recognition.cupy_performance_claim_authorized)
        self.assertFalse(recognition.measured_catalog_claim_authorized)

    def test_app_identity_kernel_fails_closed_before_planning(self) -> None:
        recognition = catalog.recognize_v4_pushdown_request(
            {
                "operator": "barnes_hut",
                "kernel": "barnes_hut",
            },
            partner="torch",
        )

        self.assertEqual("pushdown_fail_closed_app_identity_kernel", recognition.status)
        self.assertFalse(recognition.pushdown_recognized)
        self.assertTrue(recognition.fail_closed)
        self.assertEqual("rejected_app_identity_kernel_deferred", recognition.plan.status)
        self.assertIsNone(recognition.plan.api_surface)
        self.assertFalse(recognition.app_specific_native_kernel_authorized)

    def test_action_shaped_callback_fails_closed(self) -> None:
        recognition = catalog.recognize_v4_pushdown_request(
            {
                "operator": "custom_collision_response",
                "callback_shape": "custom_action",
                "mutates_shared_state": True,
                "variable_length_output": True,
                "dynamic_allocation": True,
            },
            partner="torch",
        )

        self.assertEqual("pushdown_fail_closed_action_shape", recognition.status)
        self.assertFalse(recognition.pushdown_recognized)
        self.assertTrue(recognition.fail_closed)
        self.assertEqual("rejected_action_shaped_callback_deferred", recognition.plan.status)
        self.assertFalse(recognition.raw_optix_callback_claim_authorized)
        self.assertFalse(recognition.tier3_callback_claim_authorized)

    def test_scalar_numba_callback_is_tier3_spike_only_not_pushdown(self) -> None:
        recognition = catalog.recognize_v4_pushdown_request(
            {
                "operator": "custom_force_score",
                "callback_shape": "custom_scalar_reduce",
                "numba_device_function": True,
            },
            partner="torch",
        )

        self.assertEqual("pushdown_fail_closed_tier3_spike_only", recognition.status)
        self.assertFalse(recognition.pushdown_recognized)
        self.assertTrue(recognition.fail_closed)
        self.assertEqual("tier3_spike_only_not_v4_0_release_surface", recognition.plan.status)
        self.assertTrue(recognition.plan.tier3_spike_authorized)
        self.assertFalse(recognition.tier3_callback_claim_authorized)

    def test_unsupported_logic_fails_closed_and_preserves_claim_boundaries(self) -> None:
        recognition = catalog.recognize_v4_pushdown_request(
            {
                "operator": "custom_magic_reduce",
            },
            partner="torch",
        )
        payload = recognition.as_dict()

        self.assertEqual("pushdown_fail_closed_unsupported", recognition.status)
        self.assertFalse(payload["pushdown_recognized"])
        self.assertTrue(payload["fail_closed"])
        self.assertFalse(payload["release_claim_authorized"])
        self.assertFalse(payload["broad_v4_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["measured_catalog_claim_authorized"])
        self.assertFalse(payload["embedding_c_abi_claim_authorized"])
        self.assertFalse(payload["non_python_host_binding_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
