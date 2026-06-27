from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl import v4
from rtdsl import v4_operator_catalog as catalog


class V4Goal4651PartnerCatalogPromotionTest(unittest.TestCase):
    def test_certified_partner_catalog_promotes_goal4649_and_goal4650_surfaces(self) -> None:
        rows = v4.certified_partner_catalog_v4()
        rows_by_operator = {row["operator"]: row for row in rows}

        self.assertEqual(2, len(rows))
        self.assertIn("grouped_vector_sum_f64x2", rows_by_operator)
        self.assertIn("fixed_radius_graph_component_union_3d", rows_by_operator)

        cupy = rows_by_operator["grouped_vector_sum_f64x2"]
        self.assertEqual("certified_partner", cupy["catalog_class"])
        self.assertEqual(("cupy",), cupy["measured_partners"])
        self.assertEqual(("torch", "numba", "rtdl_native"), cupy["declared_unmeasured_partners"])
        self.assertEqual("GROUPED_VECTOR_SUM_F64X2", cupy["generic_primitive"])
        self.assertEqual("partner_certified_surface_not_formal_v4_speed_win", cupy["claim_class"])
        self.assertEqual("same_contract_python_cpu_row_loop_and_optional_numba_partner_control", cupy["baseline_denominator"])
        self.assertIn("rows 262144/524288", cupy["scale"])
        self.assertGreaterEqual(cupy["min_representative_speedup"], cupy["representative_speedup_floor"])
        self.assertFalse(cupy["rt_core_operator_surface"])
        self.assertFalse(cupy["partner_migration_counts_as_v4_speed_win"])
        self.assertFalse(cupy["partner_parity_counts_as_v4_speed_win"])
        self.assertFalse(cupy["cupy_performance_claim_authorized"])
        self.assertIn("pod_live_summary.json", cupy["source_evidence"][0])

        numba = rows_by_operator["fixed_radius_graph_component_union_3d"]
        self.assertEqual(("numba",), numba["measured_partners"])
        self.assertEqual(("torch", "cupy"), numba["declared_unmeasured_partners"])
        self.assertTrue(numba["rt_core_operator_surface"])
        self.assertEqual("same_contract_embree_control_and_legacy_optix_control", numba["baseline_denominator"])
        self.assertIn("v4_goal4650_fixed_numba_continuation_certification", numba["source_evidence"][0])
        self.assertFalse(numba["whole_app_speedup_claim_authorized"])
        self.assertFalse(numba["app_specific_native_kernel_authorized"])

    def test_tier2_catalog_keeps_partner_migration_out_of_measured_rt_core_surfaces(self) -> None:
        measured = v4.measured_operator_catalog_v4()
        certified = v4.certified_partner_catalog_v4()

        self.assertEqual(10, len(measured))
        self.assertEqual(2, len(certified))
        self.assertNotIn("grouped_vector_sum_f64x2", {row["operator"] for row in measured})
        self.assertIn("grouped_vector_sum_f64x2", {row["operator"] for row in certified})
        self.assertTrue(all(row["catalog_class"] == "measured" for row in measured))
        self.assertTrue(all(row["catalog_class"] == "certified_partner" for row in certified))

    def test_planner_routes_certified_cupy_grouped_vector_sum_and_fails_closed_for_others(self) -> None:
        cupy_plan = v4.plan_operator_request_v4("grouped_vector_sum", partner="cupy")

        self.assertEqual("certified_partner_measured_ready", cupy_plan.status)
        self.assertEqual("certified_partner_surface", cupy_plan.tier)
        self.assertEqual("prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')", cupy_plan.api_surface)
        self.assertEqual("GROUPED_VECTOR_SUM_F64X2", cupy_plan.generic_primitive)
        self.assertTrue(cupy_plan.measured_partner)
        self.assertIn("must not be counted as a formal V4 speed win", cupy_plan.guidance)
        self.assertFalse(cupy_plan.release_claim_authorized)
        self.assertFalse(cupy_plan.broad_v4_speedup_claim_authorized)
        self.assertFalse(cupy_plan.whole_app_speedup_claim_authorized)
        self.assertFalse(cupy_plan.cupy_performance_claim_authorized)

        for partner in ("torch", "numba", "rtdl_native"):
            plan = v4.plan_operator_request_v4("grouped_vector_sum", partner=partner)
            self.assertEqual(catalog.V4_CERTIFIED_PARTNER_DEFERRED_STATUS, plan.status)
            self.assertEqual("certified_partner_surface", plan.tier)
            self.assertIsNone(plan.api_surface)
            self.assertFalse(plan.measured_partner)
            self.assertIn("measured for cupy only", plan.guidance)

    def test_pushdown_recognizer_understands_certified_partner_surface(self) -> None:
        recognized = v4.recognize_pushdown_request_v4(
            {
                "operator": "grouped_vector_sum",
                "dtype": "float64x2",
            },
            partner="cupy",
        )

        self.assertEqual("pushdown_recognized_certified_partner_surface", recognized.status)
        self.assertTrue(recognized.pushdown_recognized)
        self.assertFalse(recognized.fail_closed)
        self.assertEqual("certified_partner_measured_ready", recognized.plan.status)
        self.assertIn("Do not count this as formal V4-vs-V2.14 speed evidence", recognized.guidance)
        self.assertFalse(recognized.release_claim_authorized)
        self.assertFalse(recognized.cupy_performance_claim_authorized)

        blocked = v4.recognize_pushdown_request_v4({"operator": "grouped_vector_sum"}, partner="torch")
        self.assertEqual("pushdown_fail_closed_unmeasured_certified_partner", blocked.status)
        self.assertFalse(blocked.pushdown_recognized)
        self.assertTrue(blocked.fail_closed)

    def test_claim_boundary_reports_certified_partners_without_expanding_speed_claims(self) -> None:
        boundary = v4.claim_boundary_v4()

        self.assertEqual(10, len(boundary["measured_surfaces"]))
        self.assertEqual(2, boundary["certified_partner_surface_count"])
        self.assertEqual(("cupy", "numba"), boundary["certified_partners"])
        self.assertIn(
            "prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')",
            boundary["certified_partner_surfaces"],
        )
        self.assertIn(
            "v4_fixed_radius_graph_component_union_3d_device_arrays",
            boundary["certified_partner_surfaces"],
        )
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["cupy_performance_claim_authorized"])
        self.assertFalse(boundary["app_specific_native_kernel_authorized"])


if __name__ == "__main__":
    unittest.main()
