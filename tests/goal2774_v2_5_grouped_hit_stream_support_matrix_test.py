from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_hit_columns
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_payload_columns


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2774_gemini_review_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_consensus_2026-05-31.md"


class Goal2774V25GroupedHitStreamSupportMatrixTest(unittest.TestCase):
    def test_grouped_hit_stream_operation_is_declared_as_generic_contract(self) -> None:
        contract = rt.v2_5_partner_continuation_contract()
        operations = {operation["name"]: operation for operation in contract["operations"]}
        operation = operations["hit_stream_grouped_ray_id_primitive_i64"]

        self.assertEqual(operation["category"], "hit_stream_grouped_reduction")
        self.assertEqual(
            operation["input_names"],
            ("ray_ids", "primitive_ids", "row_count", "hit_event_count", "overflow", "group_count"),
        )
        self.assertEqual(
            operation["output_names"],
            (
                "group_hit_counts",
                "group_primitive_id_sum",
                "group_primitive_id_xor",
                "group_primitive_id_min",
                "group_primitive_id_max",
                "group_first_hit_row_index",
                "group_last_hit_row_index",
                "group_first_primitive_id",
                "group_last_primitive_id",
            ),
        )
        self.assertIn("generic ray_id", operation["behavior"])
        self.assertIn("row-order", operation["behavior"])
        self.assertFalse(operation["app_specific_semantics_allowed"])

    def test_support_matrix_records_cupy_preview_and_fail_closed_triton_numba(self) -> None:
        operation = "hit_stream_grouped_ray_id_primitive_i64"
        reference = rt.plan_v2_5_partner_support(operation, "reference")
        triton = rt.plan_v2_5_partner_support(operation, "triton")
        numba = rt.plan_v2_5_partner_support(operation, "numba")
        cupy = rt.plan_v2_5_partner_support(operation, "cupy")

        self.assertEqual(reference["status"], rt.V2_5_SUPPORT_STATUS_REFERENCE)
        self.assertTrue(reference["supported"])
        self.assertEqual(triton["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
        self.assertFalse(triton["supported"])
        self.assertIn("not implemented", triton["notes"])
        self.assertEqual(numba["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
        self.assertFalse(numba["supported"])
        self.assertIn("not implemented", numba["notes"])
        self.assertEqual(cupy["partner"], rt.V2_5_CONFORMANCE_PARTNER)
        self.assertEqual(cupy["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertTrue(cupy["supported"])
        self.assertIn("event-ordered grouped hit-stream", cupy["notes"])
        self.assertTrue(cupy["requires_neutral_buffer_seam"])
        self.assertTrue(cupy["requires_cuda"])
        self.assertFalse(cupy["promoted_performance_path"])
        self.assertFalse(cupy["rt_traversal_replacement_allowed"])
        self.assertFalse(cupy["public_speedup_claim_authorized"])
        self.assertFalse(cupy["true_zero_copy_claim_authorized"])

    def test_hit_stream_transfer_plan_exposes_cupy_preview_not_descriptor_only(self) -> None:
        plan = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="hit_stream_grouped_ray_id_primitive_i64",
            partner="cupy",
        )

        self.assertEqual(plan["selected_partner"], rt.V2_5_CONFORMANCE_PARTNER)
        self.assertEqual(plan["status"], "cuda_descriptor_preview")
        self.assertEqual(plan["carrier_protocol"], "cuda_array_interface_descriptor")
        self.assertTrue(plan["executable_preview_available"])
        self.assertTrue(plan["execution_allowed_without_copy"])
        self.assertFalse(plan["descriptor_only"])
        self.assertEqual(plan["runtime_action"], "cupy_preview_requires_explicit_runtime_validation")
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_preview_gate_and_support_matrix_validate_the_new_partition(self) -> None:
        gate = rt.v2_5_partner_preview_gate()
        gate_validation = rt.validate_v2_5_partner_preview_gate(gate)
        matrix = rt.v2_5_partner_support_matrix()
        matrix_validation = rt.validate_v2_5_partner_support_matrix(matrix)

        self.assertEqual(gate_validation["status"], "accept")
        self.assertEqual(matrix_validation["status"], "accept")
        self.assertEqual(
            gate["cupy_preview_operations"],
            (
                "grouped_vector_sum_f64x2",
                "hit_stream_grouped_ray_id_primitive_i64",
                "hit_stream_primitive_payload_grouped_sum_f64",
            ),
        )
        self.assertEqual(
            matrix["cupy_preview_operations"],
            (
                "grouped_vector_sum_f64x2",
                "hit_stream_grouped_ray_id_primitive_i64",
                "hit_stream_primitive_payload_grouped_sum_f64",
            ),
        )
        self.assertEqual(gate["reference_only_operations"], ())

    def test_reference_semantics_match_goal2772_signed_empty_group_sentinels(self) -> None:
        result = rt.execute_v2_5_partner_continuation_reference(
            "hit_stream_grouped_ray_id_primitive_i64",
            {
                "ray_ids": [1, 0, 1],
                "primitive_ids": [4, 3, 2],
                "row_count": 3,
                "hit_event_count": 3,
                "overflow": False,
                "group_count": 3,
            },
        )
        outputs = result["outputs"]

        self.assertEqual(outputs["group_hit_counts"], [1, 2, 0])
        self.assertEqual(outputs["group_primitive_id_sum"], [3, 6, 0])
        self.assertEqual(outputs["group_primitive_id_xor"], [3, 6, 0])
        self.assertEqual(outputs["group_primitive_id_min"], [3, 2, -1])
        self.assertEqual(outputs["group_primitive_id_max"], [3, 4, -1])
        self.assertEqual(outputs["group_first_hit_row_index"], [1, 0, -1])
        self.assertEqual(outputs["group_last_hit_row_index"], [1, 2, -1])
        self.assertEqual(outputs["group_first_primitive_id"], [3, 4, -1])
        self.assertEqual(outputs["group_last_primitive_id"], [3, 2, -1])

    def test_goal2774_report_records_boundary(self) -> None:
        report = REPORT.read_text()
        review = REVIEW.read_text()
        consensus = CONSENSUS.read_text()

        self.assertIn("hit_stream_grouped_ray_id_primitive_i64", report)
        self.assertIn("CuPy preview", report)
        self.assertIn("Triton and Numba fail closed", report)
        self.assertIn("no public speedup", report)
        self.assertIn("**Verdict:** accept", review)
        self.assertIn("`accept`", consensus)


if __name__ == "__main__":
    unittest.main()
