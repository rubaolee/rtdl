from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl.v4 as rt_v4
import rtdsl.v4_operator_catalog as catalog


class _DummyExecutor:
    def __init__(self) -> None:
        self.closed = False

    def run(self):
        return {"accepted_count": 7, "metadata": {"executor": "dummy"}}

    def close(self) -> None:
        self.closed = True


class V4Goal4716CustomPredicateEarlyExitProductizationTest(unittest.TestCase):
    def test_claim_boundary_records_measured_focused_evidence_without_release(self) -> None:
        boundary = rt_v4.ray_triangle_custom_predicate_early_exit_claim_boundary_v4()

        self.assertEqual(rt_v4.V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE, boundary["v4_api_surface"])
        self.assertEqual("numba", boundary["partner"])
        self.assertTrue(boundary["measured_partner"])
        self.assertTrue(boundary["constrained_user_predicate_authorized"])
        self.assertAlmostEqual(3.608025018751732, boundary["goal4715_primary_v3_speedup_geomean"])
        self.assertAlmostEqual(1.9761904761904763, boundary["goal4715_min_primary_v3_speedup"])
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["arbitrary_python_callback_authorized"])
        self.assertFalse(boundary["raw_optix_callback_claim_authorized"])

    def test_catalog_promotes_surface_as_measured_operator_pushdown(self) -> None:
        rows = {row["operator"]: row for row in catalog.measured_v4_tier2_operator_catalog()}
        row = rows[catalog.V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT]

        self.assertEqual("measured", row["catalog_class"])
        self.assertEqual(rt_v4.V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE, row["api_surface"])
        self.assertEqual(("numba",), row["measured_partners"])
        self.assertTrue(row["constrained_user_predicate_authorized"])
        self.assertFalse(row["arbitrary_callback_authorized"])
        self.assertFalse(row["release_claim_authorized"])
        self.assertEqual("operator_pushdown_vs_materialized_device_fallback", row["comparison_class"])

    def test_planner_requires_numba_boolean_device_predicate(self) -> None:
        plan = rt_v4.plan_operator_request_v4(
            "custom_predicate_early_exit",
            partner="numba",
            callback_shape="pure_boolean_numba_cabi_device_function",
            numba_device_function=True,
        )

        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_operator_pushdown", plan.tier)
        self.assertEqual(rt_v4.V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE, plan.api_surface)
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.tier3_callback_claim_authorized)

    def test_planner_fails_closed_for_wrong_partner_or_unsafe_callback(self) -> None:
        wrong_partner = rt_v4.plan_operator_request_v4(
            "custom_predicate_early_exit",
            partner="cupy",
            callback_shape="pure_boolean_numba_cabi_device_function",
            numba_device_function=True,
        )
        self.assertEqual("tier2_declared_unmeasured_partner", wrong_partner.status)
        self.assertIsNone(wrong_partner.api_surface)

        unsafe = rt_v4.plan_operator_request_v4(
            "custom_predicate_early_exit",
            partner="numba",
            callback_shape="pure_boolean_numba_cabi_device_function",
            numba_device_function=True,
            mutates_shared_state=True,
        )
        self.assertEqual("rejected_action_shaped_callback_deferred", unsafe.status)
        self.assertIsNone(unsafe.api_surface)

        missing_numba = rt_v4.plan_operator_request_v4(
            "custom_predicate_early_exit",
            partner="numba",
            callback_shape="pure_boolean_numba_cabi_device_function",
            numba_device_function=False,
        )
        self.assertEqual("rejected_missing_constrained_numba_predicate", missing_numba.status)

    def test_recognizer_routes_constrained_predicate_and_rejects_arbitrary_callback(self) -> None:
        recognized = rt_v4.recognize_pushdown_request_v4(
            {
                "operator": "custom_predicate_early_exit",
                "callback_shape": "pure_boolean_numba_cabi_device_function",
                "numba_device_function": True,
            },
            partner="numba",
        )
        self.assertEqual("pushdown_recognized_measured_tier2", recognized.status)
        self.assertTrue(recognized.pushdown_recognized)
        self.assertFalse(recognized.raw_optix_callback_claim_authorized)

        rejected = rt_v4.recognize_pushdown_request_v4(
            {
                "operator": "custom_predicate_early_exit",
                "callback_shape": "python_callable",
                "numba_device_function": False,
            },
            partner="numba",
        )
        self.assertEqual("pushdown_fail_closed_unsupported", rejected.status)
        self.assertFalse(rejected.pushdown_recognized)
        self.assertTrue(rejected.fail_closed)

    def test_public_wrapper_adds_metadata_without_exposing_optix_handles(self) -> None:
        executor = _DummyExecutor()
        session = rt_v4.prepare_ray_triangle_custom_predicate_early_exit_3d_numba_v4(executor)
        result = session.run()

        self.assertEqual(7, result["accepted_count"])
        self.assertEqual(rt_v4.V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE, result["metadata"]["adapter"])
        self.assertFalse(result["metadata"]["raw_optix_callback_claim_authorized"])
        session.close()
        self.assertTrue(executor.closed)


if __name__ == "__main__":
    unittest.main()
