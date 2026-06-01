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
                "grouped_vector_sum_f64x2",
                "segmented_min_f64",
                "segmented_max_f64",
                "compact_mask_i64",
                "edge_list_components_i64",
                "bounded_collect_finalize_i64",
                "grouped_argmin_f64",
                "grouped_argmax_f64",
                "grouped_topk_f64",
                "hit_stream_grouped_ray_id_primitive_i64",
                "hit_stream_primitive_payload_grouped_sum_f64",
            },
        )
        serialized = repr(rt.v2_5_partner_continuation_contract()).lower()
        for forbidden in rt.V2_4_FORBIDDEN_NATIVE_APP_TOKENS:
            self.assertNotIn(forbidden, serialized)

        operations = {
            operation["name"]: operation
            for operation in rt.v2_5_partner_continuation_contract()["operations"]
        }
        for operation_name in (
            "segmented_count_i64",
            "segmented_sum_f64",
            "grouped_vector_sum_f64x2",
            "segmented_min_f64",
            "segmented_max_f64",
            "bounded_collect_finalize_i64",
            "grouped_argmin_f64",
            "grouped_argmax_f64",
            "grouped_topk_f64",
        ):
            self.assertIn(rt.V2_5_GROUP_ID_VALIDATION_CONTRACT, operations[operation_name]["behavior"])
        hit_stream = operations["hit_stream_grouped_ray_id_primitive_i64"]
        self.assertEqual(hit_stream["category"], "hit_stream_grouped_reduction")
        self.assertIn("ray_id", hit_stream["behavior"])
        self.assertIn("row-order", hit_stream["behavior"])
        self.assertIn("-1 sentinels", hit_stream["behavior"])
        payload_sum = operations["hit_stream_primitive_payload_grouped_sum_f64"]
        self.assertEqual(payload_sum["category"], "hit_stream_payload_reduction")
        self.assertIn("primitive payload columns", payload_sum["behavior"])
        self.assertIn("producer overflow fails closed", payload_sum["behavior"])
        components = operations["edge_list_components_i64"]
        self.assertEqual(components["category"], "component_labeling")
        self.assertIn("source and target node ids", components["behavior"])

    def test_planner_prefers_triton_then_numba_then_reference(self):
        triton = rt.plan_v2_5_partner_continuation(
            "segmented_sum_f64",
            available_partners=("numba", "triton"),
        )
        self.assertEqual(triton.partner, "triton")
        self.assertEqual(triton.status, "preview_not_promoted")

        numba = rt.plan_v2_5_partner_continuation(
            "segmented_sum_f64",
            available_partners=("numba",),
        )
        self.assertEqual(numba.partner, "numba")
        self.assertEqual(numba.status, "preview_not_promoted")

        compact_preview = rt.plan_v2_5_partner_continuation(
            "compact_mask_i64",
            available_partners=("triton",),
        )
        self.assertEqual(compact_preview.partner, "triton")
        self.assertEqual(compact_preview.status, "preview_not_promoted")

        reference = rt.plan_v2_5_partner_continuation(
            "segmented_sum_f64",
            available_partners=(),
        )
        self.assertEqual(reference.partner, "python_reference")
        self.assertEqual(reference.status, "reference_contract")

        cupy_hit_stream = rt.plan_v2_5_partner_continuation(
            "hit_stream_grouped_ray_id_primitive_i64",
            available_partners=("cupy",),
        )
        self.assertEqual(cupy_hit_stream.partner, "cupy_conformance")
        self.assertEqual(cupy_hit_stream.status, "preview_not_promoted")

        cupy_hit_stream_over_triton_descriptor = rt.plan_v2_5_partner_continuation(
            "hit_stream_grouped_ray_id_primitive_i64",
            available_partners=("triton", "cupy"),
        )
        self.assertEqual(cupy_hit_stream_over_triton_descriptor.partner, "cupy_conformance")
        self.assertEqual(cupy_hit_stream_over_triton_descriptor.status, "preview_not_promoted")

        cupy_payload_hit_stream = rt.plan_v2_5_partner_continuation(
            "hit_stream_primitive_payload_grouped_sum_f64",
            available_partners=("cupy",),
        )
        self.assertEqual(cupy_payload_hit_stream.partner, "cupy_conformance")
        self.assertEqual(cupy_payload_hit_stream.status, "preview_not_promoted")

        unsupported_triton = rt.plan_v2_5_partner_continuation(
            "hit_stream_grouped_ray_id_primitive_i64",
            available_partners=("triton",),
        )
        self.assertEqual(unsupported_triton.partner, "python_reference")
        self.assertEqual(unsupported_triton.status, "reference_contract")

        unsupported_numba = rt.plan_v2_5_partner_continuation(
            "compact_mask_i64",
            available_partners=("numba",),
        )
        self.assertEqual(unsupported_numba.partner, "python_reference")
        self.assertEqual(unsupported_numba.status, "reference_contract")

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

        vector_sum = rt.execute_v2_5_partner_continuation_reference(
            "grouped_vector_sum_f64x2",
            {
                "group_ids": [0, 2, 2, 1, 0],
                "values_x": [1.0, 2.5, 3.5, 4.0, 6.0],
                "values_y": [0.5, -1.0, 2.0, 3.0, -0.5],
                "group_count": 4,
            },
        )
        self.assertEqual(vector_sum["outputs"]["sum_x"], [7.0, 4.0, 6.0, 0.0])
        self.assertEqual(vector_sum["outputs"]["sum_y"], [0.0, 3.0, 1.0, 0.0])

    def test_reference_segmented_min_and_max(self):
        min_result = rt.execute_v2_5_partner_continuation_reference(
            "segmented_min_f64",
            {"group_ids": [0, 2, 2, 1, 0], "values": [1.0, 2.5, 3.5, 4.0, 6.0], "group_count": 4},
        )
        self.assertEqual(min_result["outputs"]["group_ids"], [0, 1, 2])
        self.assertEqual(min_result["outputs"]["mins"], [1.0, 4.0, 2.5])
        self.assertEqual(min_result["outputs"]["missing_group_ids"], [3])

        max_result = rt.execute_v2_5_partner_continuation_reference(
            "segmented_max_f64",
            {"group_ids": [0, 2, 2, 1, 0], "values": [1.0, 2.5, 3.5, 4.0, 6.0], "group_count": 4},
        )
        self.assertEqual(max_result["outputs"]["group_ids"], [0, 1, 2])
        self.assertEqual(max_result["outputs"]["maxes"], [6.0, 4.0, 3.5])
        self.assertEqual(max_result["outputs"]["missing_group_ids"], [3])

        with self.assertRaisesRegex(ValueError, "reject NaN"):
            rt.execute_v2_5_partner_continuation_reference(
                "segmented_min_f64",
                {"group_ids": [0], "values": [float("nan")], "group_count": 1},
            )

    def test_reference_compact_mask_and_grouped_argmin(self):
        compact = rt.execute_v2_5_partner_continuation_reference(
            "compact_mask_i64",
            {"values": [10, 20, 30, 40], "mask": [False, True, True, False]},
        )
        self.assertEqual(compact["outputs"]["values"], [20, 30])
        self.assertEqual(compact["outputs"]["original_indices"], [1, 2])

        components = rt.execute_v2_5_partner_continuation_reference(
            "edge_list_components_i64",
            {
                "source_ids": [0, 1, 3],
                "target_ids": [1, 2, 4],
                "node_count": 6,
                "max_iterations": 6,
            },
        )
        self.assertEqual(components["outputs"]["component_ids"], [0, 0, 0, 3, 3, 5])

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

        argmax = rt.execute_v2_5_partner_continuation_reference(
            "grouped_argmax_f64",
            {
                "group_ids": [0, 0, 1, 1, 1],
                "item_ids": [9, 8, 2, 1, 3],
                "scores": [4.0, 4.0, 7.0, 9.0, 9.0],
                "group_count": 3,
            },
        )
        self.assertEqual(argmax["outputs"]["group_ids"], [0, 1])
        self.assertEqual(argmax["outputs"]["item_ids"], [8, 1])
        self.assertEqual(argmax["outputs"]["scores"], [4.0, 9.0])
        self.assertEqual(argmax["outputs"]["missing_group_ids"], [2])

        topk = rt.execute_v2_5_partner_continuation_reference(
            "grouped_topk_f64",
            {
                "group_ids": [0, 0, 0, 1, 1, 1, 1],
                "item_ids": [9, 8, 8, 2, 1, 3, 4],
                "scores": [4.0, 4.0, 3.5, 7.0, 9.0, 9.0, 6.0],
                "group_count": 3,
                "k": 2,
            },
        )
        self.assertEqual(topk["outputs"]["group_ids"], [0, 0, 1, 1])
        self.assertEqual(topk["outputs"]["item_ids"], [8, 9, 4, 2])
        self.assertEqual(topk["outputs"]["scores"], [3.5, 4.0, 6.0, 7.0])
        self.assertEqual(topk["outputs"]["ranks"], [1, 2, 1, 2])
        self.assertEqual(topk["outputs"]["row_offsets"], [0, 2, 4, 4])
        self.assertEqual(topk["outputs"]["missing_group_ids"], [2])

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

    def test_reference_hit_stream_grouped_ray_id_primitive_reduction(self):
        result = rt.execute_v2_5_partner_continuation_reference(
            "hit_stream_grouped_ray_id_primitive_i64",
            {
                "ray_ids": [0, 2, 0, 2],
                "primitive_ids": [5, 7, 3, 7],
                "row_count": 4,
                "hit_event_count": 4,
                "overflow": False,
                "group_count": 3,
            },
        )
        outputs = result["outputs"]
        self.assertEqual(outputs["group_hit_counts"], [2, 0, 2])
        self.assertEqual(outputs["group_primitive_id_sum"], [8, 0, 14])
        self.assertEqual(outputs["group_primitive_id_xor"], [6, 0, 0])
        self.assertEqual(outputs["group_primitive_id_min"], [3, -1, 7])
        self.assertEqual(outputs["group_primitive_id_max"], [5, -1, 7])
        self.assertEqual(outputs["group_first_hit_row_index"], [0, -1, 1])
        self.assertEqual(outputs["group_last_hit_row_index"], [2, -1, 3])
        self.assertEqual(outputs["group_first_primitive_id"], [5, -1, 7])
        self.assertEqual(outputs["group_last_primitive_id"], [3, -1, 7])

        with self.assertRaisesRegex(
            rt.PartnerContinuationOverflowError,
            "failure_mode=fail_closed_overflow.*partial_result_returned=False",
        ):
            rt.execute_v2_5_partner_continuation_reference(
                "hit_stream_grouped_ray_id_primitive_i64",
                {
                    "ray_ids": [0],
                    "primitive_ids": [1],
                    "row_count": 1,
                    "hit_event_count": 2,
                    "overflow": True,
                    "group_count": 1,
                },
            )

        payload_sum = rt.execute_v2_5_partner_continuation_reference(
            "hit_stream_primitive_payload_grouped_sum_f64",
            {
                "ray_ids": [0, 2, 0, 2],
                "primitive_ids": [0, 1, 0, 1],
                "row_count": 4,
                "hit_event_count": 4,
                "overflow": False,
                "primitive_group_ids": [0, 2],
                "primitive_values": [10.5, 1.25],
                "primitive_count": 2,
                "group_count": 3,
            },
        )
        self.assertEqual(payload_sum["outputs"]["group_hit_counts"], [2, 0, 2])
        self.assertEqual(payload_sum["outputs"]["group_payload_sums"], [21.0, 0.0, 2.5])

    def test_group_id_bounds_are_rejected_by_reference_and_triton_precheck(self):
        reference_cases = (
            ("segmented_count_i64", {"group_ids": [-1, 0], "group_count": 2}),
            ("segmented_sum_f64", {"group_ids": [0, 2], "values": [1.0, 2.0], "group_count": 2}),
            (
                "grouped_vector_sum_f64x2",
                {"group_ids": [0, 2], "values_x": [1.0, 2.0], "values_y": [3.0, 4.0], "group_count": 2},
            ),
            ("segmented_min_f64", {"group_ids": [0, 2], "values": [1.0, 2.0], "group_count": 2}),
            ("segmented_max_f64", {"group_ids": [0, 2], "values": [1.0, 2.0], "group_count": 2}),
            (
                "bounded_collect_finalize_i64",
                {"group_ids": [0, 2], "item_ids": [10, 20], "group_count": 2, "k": 2},
            ),
            (
                "edge_list_components_i64",
                {"source_ids": [0, 2], "target_ids": [1, 0], "node_count": 2, "max_iterations": 2},
            ),
            (
                "grouped_argmin_f64",
                {"group_ids": [0, 2], "item_ids": [10, 20], "scores": [1.0, 2.0], "group_count": 2},
            ),
            (
                "grouped_argmax_f64",
                {"group_ids": [0, 2], "item_ids": [10, 20], "scores": [1.0, 2.0], "group_count": 2},
            ),
            (
                "grouped_topk_f64",
                {"group_ids": [0, 2], "item_ids": [10, 20], "scores": [1.0, 2.0], "group_count": 2, "k": 1},
            ),
        )
        for operation, inputs in reference_cases:
            with self.subTest(operation=operation, backend="reference"):
                with self.assertRaisesRegex(
                    ValueError,
                    r"group ids must be in \[0, group_count\)|source_ids and target_ids must be in \[0, node_count\)",
                ):
                    rt.execute_v2_5_partner_continuation_reference(operation, inputs)

        if not rt.triton_partner_available():
            return

        import torch

        triton_cases = (
            ("segmented_count_i64", {"group_ids": torch.tensor([-1, 0], dtype=torch.int64, device="cuda"), "group_count": 2}),
            (
                "segmented_sum_f64",
                {
                    "group_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "values": torch.tensor([1.0, 2.0], dtype=torch.float64, device="cuda"),
                    "group_count": 2,
                },
            ),
            (
                "grouped_vector_sum_f64x2",
                {
                    "group_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "values_x": torch.tensor([1.0, 2.0], dtype=torch.float64, device="cuda"),
                    "values_y": torch.tensor([3.0, 4.0], dtype=torch.float64, device="cuda"),
                    "group_count": 2,
                },
            ),
            (
                "segmented_min_f64",
                {
                    "group_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "values": torch.tensor([1.0, 2.0], dtype=torch.float64, device="cuda"),
                    "group_count": 2,
                },
            ),
            (
                "segmented_max_f64",
                {
                    "group_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "values": torch.tensor([1.0, 2.0], dtype=torch.float64, device="cuda"),
                    "group_count": 2,
                },
            ),
            (
                "bounded_collect_finalize_i64",
                {
                    "group_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "item_ids": torch.tensor([10, 20], dtype=torch.int64, device="cuda"),
                    "group_count": 2,
                    "k": 2,
                },
            ),
            (
                "edge_list_components_i64",
                {
                    "source_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "target_ids": torch.tensor([1, 0], dtype=torch.int64, device="cuda"),
                    "node_count": 2,
                    "max_iterations": 2,
                },
            ),
            (
                "grouped_argmin_f64",
                {
                    "group_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "item_ids": torch.tensor([10, 20], dtype=torch.int64, device="cuda"),
                    "scores": torch.tensor([1.0, 2.0], dtype=torch.float64, device="cuda"),
                    "group_count": 2,
                },
            ),
            (
                "grouped_argmax_f64",
                {
                    "group_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "item_ids": torch.tensor([10, 20], dtype=torch.int64, device="cuda"),
                    "scores": torch.tensor([1.0, 2.0], dtype=torch.float64, device="cuda"),
                    "group_count": 2,
                },
            ),
            (
                "grouped_topk_f64",
                {
                    "group_ids": torch.tensor([0, 2], dtype=torch.int64, device="cuda"),
                    "item_ids": torch.tensor([10, 20], dtype=torch.int64, device="cuda"),
                    "scores": torch.tensor([1.0, 2.0], dtype=torch.float64, device="cuda"),
                    "group_count": 2,
                    "k": 1,
                },
            ),
        )
        for operation, inputs in triton_cases:
            with self.subTest(operation=operation, backend="triton"):
                with self.assertRaisesRegex(
                    ValueError,
                    r"group_ids must be in \[0, group_count\)|source_ids and target_ids must be in \[0, node_count\)",
                ):
                    rt.run_triton_partner_continuation(operation, inputs)

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
