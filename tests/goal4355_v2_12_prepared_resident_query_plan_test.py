from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4355_v2_12_prepared_resident_query_plan_2026-06-12.md"


class Goal4355V212PreparedResidentQueryPlanTest(unittest.TestCase):
    def test_plan_validates_and_keeps_claims_false(self) -> None:
        plan = rt.v2_12_prepared_resident_query_plan()
        summary = rt.summarize_v2_12_prepared_resident_query_plan(plan)
        validation = rt.validate_v2_12_prepared_resident_query_plan(plan)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        self.assertGreaterEqual(summary["row_count"], 5)
        self.assertTrue(summary["all_require_native_repeat_loop"])
        self.assertTrue(summary["all_require_duration_bounded_timing"])
        self.assertTrue(summary["all_require_same_prepared_abi"])
        self.assertTrue(summary["all_forbid_row_materialization"])
        self.assertEqual(summary["required_backends"], ("optix", "embree"))

        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
        ):
            self.assertFalse(summary[flag], flag)

    def test_spatial_rayjoin_pip_exact_route_is_first_optimization_debt(self) -> None:
        plan = rt.v2_12_prepared_resident_query_plan()
        pip = plan[0]

        self.assertEqual(pip["row_id"], "spatial_rayjoin_pip_exact_native_resident_scalar_count")
        self.assertEqual(pip["priority"], 1)
        self.assertEqual(pip["benchmark_app"], "spatial_rayjoin")
        self.assertEqual(pip["workload"], "pip")
        self.assertEqual(pip["current_route"], "prepared_exact_closed_shape_membership_scalar_count")
        self.assertEqual(pip["target_route"], "native_prepared_exact_point_in_polygon_scalar_count")
        self.assertIn("0.613610 ms", pip["current_gap"])
        self.assertIn("7.081935 ms", pip["current_gap"])
        self.assertIn("relation-status", pip["current_gap"])
        self.assertIn("rtdl_optix_prepared_exact_point_in_polygon_count_2d", pip["target_native_symbols"])
        self.assertIn("rtdl_embree_point_primitive_anyhit_2d_count", pip["target_native_symbols"])
        self.assertTrue(pip["requires_exactness_gate"])

    def test_every_row_is_backend_parity_and_native_hot_loop_work(self) -> None:
        for row in rt.v2_12_prepared_resident_query_plan():
            with self.subTest(row_id=row["row_id"]):
                self.assertEqual(row["required_backend_parity"], ("optix", "embree"))
                self.assertTrue(row["requires_native_repeat_loop"])
                self.assertTrue(row["requires_duration_bounded_timing"])
                self.assertTrue(row["requires_cold_hot_phase_split"])
                self.assertTrue(row["requires_same_prepared_abi"])
                self.assertTrue(row["requires_no_row_materialization"])
                self.assertFalse(row["ready_to_measure"])
                self.assertFalse(row["release_authorized"])
                self.assertNotIn("materializing rows", row["fairness_contract"].lower())

    def test_invalid_plan_rows_are_rejected(self) -> None:
        bad = dict(rt.v2_12_prepared_resident_query_plan()[0])
        bad["requires_duration_bounded_timing"] = False
        bad["public_speedup_claim_authorized"] = True

        validation = rt.validate_v2_12_prepared_resident_query_plan((bad,))
        self.assertEqual(validation["status"], "reject")
        self.assertIn(
            "spatial_rayjoin_pip_exact_native_resident_scalar_count: "
            "requires_duration_bounded_timing must be true",
            validation["errors"],
        )
        self.assertIn(
            "spatial_rayjoin_pip_exact_native_resident_scalar_count: "
            "public_speedup_claim_authorized must remain false",
            validation["errors"],
        )

    def test_package_exports_and_report_document_the_v2_12_start(self) -> None:
        self.assertIn("v2_12_prepared_resident_query_plan", rt.__all__)
        self.assertIn("validate_v2_12_prepared_resident_query_plan", rt.__all__)
        self.assertEqual(
            rt.V2_12_PREPARED_RESIDENT_QUERY_PLAN_VERSION,
            "rtdl.v2_12.prepared_resident_query_plan.goal4355.v1",
        )

        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal4355",
            "RayJoin PIP",
            "0.613610 ms",
            "7.081935 ms",
            "native repeat loop",
            "same prepared ABI",
            "duration-bounded",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
