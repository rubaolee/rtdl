from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_operator_catalog as catalog


class V4OperatorCatalogTest(unittest.TestCase):
    def test_measured_tier2_operator_is_planned_as_fused_surface(self) -> None:
        plan = catalog.plan_v4_operator_request("fixed-radius", partner="torch")

        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_fused_operator", plan.tier)
        self.assertEqual("v4_fixed_radius_count_threshold_2d_device_arrays", plan.api_surface)
        self.assertEqual("FIXED_RADIUS_COUNT_THRESHOLD_2D", plan.generic_primitive)
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.tier3_callback_claim_authorized)
        self.assertFalse(plan.app_specific_native_kernel_authorized)

    def test_cupy_tier2_partner_is_declared_but_unmeasured(self) -> None:
        plan = catalog.plan_v4_operator_request("grouped_argmin", partner="cupy")

        self.assertEqual("tier2_declared_unmeasured_partner", plan.status)
        self.assertIsNone(plan.api_surface)
        self.assertFalse(plan.measured_partner)
        self.assertIn("measured for Torch only", plan.guidance)
        self.assertIn("No V4.0 API surface", plan.guidance)
        self.assertFalse(plan.cupy_performance_claim_authorized)
        self.assertFalse(plan.non_python_host_binding_claim_authorized)
        self.assertFalse(plan.broad_v4_speedup_claim_authorized)

    def test_numba_scalar_callback_is_spike_only_not_supported_surface(self) -> None:
        plan = catalog.plan_v4_operator_request(
            "custom_force_score",
            callback_shape="custom_scalar_reduce",
            numba_device_function=True,
            partner="torch",
        )

        self.assertEqual("tier3_spike_only_not_v4_0_release_surface", plan.status)
        self.assertEqual("tier3_numba_ptx_spike", plan.tier)
        self.assertTrue(plan.tier3_spike_authorized)
        self.assertFalse(plan.tier3_callback_claim_authorized)
        self.assertFalse(plan.release_claim_authorized)
        self.assertIsNone(plan.api_surface)

    def test_action_shaped_callback_is_rejected_not_wrapped_as_optix(self) -> None:
        plan = catalog.plan_v4_operator_request(
            "custom_collision_response",
            callback_shape="custom_action",
            mutates_shared_state=True,
            variable_length_output=True,
            dynamic_allocation=True,
            partner="torch",
        )

        self.assertEqual("rejected_action_shaped_callback_deferred", plan.status)
        self.assertEqual("unsupported_v4_0_deferred", plan.tier)
        self.assertIn("shared mutation", plan.guidance)
        self.assertIn("dynamic allocation", plan.guidance)
        self.assertIn("variable-length output", plan.guidance)
        self.assertIn("does not expose raw OptiX callbacks", plan.guidance)
        self.assertFalse(plan.tier3_spike_authorized)
        self.assertFalse(plan.app_specific_native_kernel_authorized)

    def test_catalog_rows_keep_release_and_app_kernel_claims_false(self) -> None:
        rows = catalog.measured_v4_tier2_operator_catalog()
        self.assertEqual(3, len(rows))
        surfaces = {row["api_surface"] for row in rows}
        self.assertIn("v4_ray_triangle_any_hit_flags_2d_device_arrays", surfaces)
        self.assertTrue(all(row["measured_partners"] == ("torch",) for row in rows))
        self.assertTrue(all(row["release_claim_authorized"] is False for row in rows))
        self.assertTrue(all(row["app_specific_native_kernel_authorized"] is False for row in rows))

    def test_invalid_partner_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "partner must be one of"):
            catalog.plan_v4_operator_request("any_hit", partner="numpy")


if __name__ == "__main__":
    unittest.main()
