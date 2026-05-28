from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2662V25PartnerContinuationContractTest(unittest.TestCase):
    def test_contract_is_triton_first_with_numba_fallback_but_no_perf_claim(self):
        contract = rt.v2_5_partner_continuation_contract()
        validation = rt.validate_v2_5_partner_continuation_contract(contract)

        self.assertIn("v2_5_partner_continuation_contract", rt.__all__)
        self.assertIn("execute_v2_5_partner_continuation_reference", rt.__all__)
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(contract["primary_partner"], "triton")
        self.assertEqual(contract["fallback_partner"], "numba")
        self.assertFalse(contract["performance_path_authorized"])
        self.assertFalse(contract["rt_traversal_replacement_allowed"])
        self.assertFalse(contract["rawkernel_required_allowed"])
        self.assertFalse(contract["native_engine_app_specific_vocab_allowed"])
        self.assertTrue(contract["phase_timing_required"])

    def test_operation_set_is_generic_and_app_agnostic(self):
        names = set(rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)

        self.assertEqual(
            names,
            {
                "segmented_count_i64",
                "segmented_sum_f64",
                "compact_mask_i64",
                "bounded_collect_finalize_i64",
                "grouped_argmin_f64",
            },
        )
        serialized = repr(rt.v2_5_partner_continuation_contract()).lower()
        for forbidden in rt.V2_4_FORBIDDEN_NATIVE_APP_TOKENS:
            self.assertNotIn(forbidden, serialized)

    def test_planner_prefers_triton_then_numba_then_reference(self):
        triton = rt.plan_v2_5_partner_continuation(
            "segmented_sum_f64",
            available_partners=("numba", "triton"),
        )
        self.assertEqual(triton.partner, "triton")
        self.assertEqual(triton.status, "partner_descriptor_only")

        numba = rt.plan_v2_5_partner_continuation(
            "segmented_sum_f64",
            available_partners=("numba",),
        )
        self.assertEqual(numba.partner, "numba")
        self.assertEqual(numba.status, "partner_descriptor_only")

        reference = rt.plan_v2_5_partner_continuation(
            "segmented_sum_f64",
            available_partners=(),
        )
        self.assertEqual(reference.partner, "python_reference")
        self.assertEqual(reference.status, "reference_contract")

    def test_spec_rejects_rt_replacement_rawkernel_and_promotion(self):
        with self.assertRaisesRegex(ValueError, "must not replace"):
            rt.RtdlPartnerContinuationSpec(
                operation="segmented_count_i64",
                replaces_rt_traversal=True,
            )
        with self.assertRaisesRegex(ValueError, "RawKernel"):
            rt.RtdlPartnerContinuationSpec(
                operation="segmented_count_i64",
                raw_kernel_required=True,
            )
        with self.assertRaisesRegex(ValueError, "promoted performance"):
            rt.RtdlPartnerContinuationSpec(
                operation="segmented_count_i64",
                promoted_performance_path=True,
            )
        with self.assertRaisesRegex(ValueError, "app-agnostic"):
            rt.RtdlPartnerContinuationSpec(
                operation="segmented_count_i64",
                app_specific_semantics_allowed=True,
            )

    def test_non_reference_partner_is_descriptor_only_until_evidence(self):
        with self.assertRaisesRegex(ValueError, "descriptor-only"):
            rt.RtdlPartnerContinuationSpec(
                operation="segmented_count_i64",
                partner="triton",
                status="reference_contract",
            )

        spec = rt.RtdlPartnerContinuationSpec(
            operation="segmented_count_i64",
            partner="triton",
            status="partner_descriptor_only",
        )
        metadata = spec.to_metadata()
        self.assertEqual(metadata["partner"], "triton")
        self.assertFalse(metadata["replaces_rt_traversal"])
        self.assertFalse(metadata["raw_kernel_required"])
        self.assertFalse(metadata["promoted_performance_path"])

    def test_reference_segmented_count_and_sum(self):
        count_result = rt.execute_v2_5_partner_continuation_reference(
            "segmented_count_i64",
            {"group_ids": [0, 2, 2, 1, 0], "group_count": 4},
        )
        self.assertEqual(count_result["outputs"]["counts"], [2, 1, 2, 0])
        self.assertEqual(count_result["phase_timing_validation"]["status"], "accept")

        sum_result = rt.execute_v2_5_partner_continuation_reference(
            "segmented_sum_f64",
            {"group_ids": [0, 2, 2, 1, 0], "values": [1.0, 2.5, 3.5, 4.0, 6.0], "group_count": 4},
        )
        self.assertEqual(sum_result["outputs"]["sums"], [7.0, 4.0, 6.0, 0.0])

    def test_reference_compact_mask_and_grouped_argmin(self):
        compact = rt.execute_v2_5_partner_continuation_reference(
            "compact_mask_i64",
            {"values": [10, 20, 30, 40], "mask": [False, True, True, False]},
        )
        self.assertEqual(compact["outputs"]["values"], [20, 30])
        self.assertEqual(compact["outputs"]["original_indices"], [1, 2])

        argmin = rt.execute_v2_5_partner_continuation_reference(
            "grouped_argmin_f64",
            {
                "group_ids": [0, 0, 1, 1, 1],
                "item_ids": [9, 8, 2, 1, 3],
                "scores": [4.0, 4.0, 7.0, 5.0, 5.0],
                "group_count": 3,
            },
        )
        self.assertEqual(argmin["outputs"]["group_ids"], [0, 1])
        self.assertEqual(argmin["outputs"]["item_ids"], [8, 1])
        self.assertEqual(argmin["outputs"]["scores"], [4.0, 5.0])
        self.assertEqual(argmin["outputs"]["missing_group_ids"], [2])

    def test_bounded_collect_finalize_is_fail_closed(self):
        ok = rt.execute_v2_5_partner_continuation_reference(
            "bounded_collect_finalize_i64",
            {
                "group_ids": [0, 1, 1, 2],
                "item_ids": [10, 20, 21, 30],
                "group_count": 3,
                "k": 2,
                "total_row_capacity": 4,
            },
        )
        self.assertEqual(ok["outputs"]["group_ids"], [0, 1, 1, 2])
        self.assertEqual(ok["outputs"]["item_ids"], [10, 20, 21, 30])
        self.assertEqual(ok["outputs"]["row_offsets"], [0, 1, 3, 4])

        with self.assertRaisesRegex(
            rt.PartnerContinuationOverflowError,
            "failure_mode=fail_closed_overflow.*partial_result_returned=False",
        ):
            rt.execute_v2_5_partner_continuation_reference(
                "bounded_collect_finalize_i64",
                {
                    "group_ids": [1, 1, 1],
                    "item_ids": [20, 21, 22],
                    "group_count": 3,
                    "k": 2,
                },
            )

    def test_docs_record_goal2662_boundary(self):
        report = (ROOT / "docs/reports/goal2662_v2_5_partner_continuation_contract_2026-05-27.md").read_text()
        boundaries = (ROOT / "docs/partner_acceleration_boundaries.md").read_text()

        self.assertIn("Triton", report)
        self.assertIn("Numba", report)
        self.assertIn("descriptor-only", report)
        self.assertIn("not a performance claim", report)
        self.assertIn("goal2662_v2_5_partner_continuation_contract_2026-05-27.md", boundaries)


if __name__ == "__main__":
    unittest.main()
