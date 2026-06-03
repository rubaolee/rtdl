from __future__ import annotations

from pathlib import Path
import unittest
from unittest import mock

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3111_v2_8_segmented_typed_stream_adapter_2026-06-03.md"


class Goal3111V28SegmentedTypedStreamAdapterTest(unittest.TestCase):
    def test_adapter_summary_is_internal_and_non_authorizing(self) -> None:
        summary = rt.v2_8_segmented_typed_stream_adapter_summary()

        self.assertEqual(summary["adapter_version"], rt.V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_VERSION)
        self.assertEqual(summary["target"], rt.V2_8_FIRST_RUNTIME_TARGET)
        self.assertEqual(summary["materialization"], "host_reference_contract_adapter")
        self.assertFalse(summary["native_producer_promoted"])
        self.assertFalse(summary["partner_consumer_promoted"])
        self.assertFalse(summary["device_resident_result_stream_proven"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["rt_core_speedup_claim_authorized"])
        self.assertFalse(summary["hidden_dispatch_allowed"])
        self.assertFalse(summary["automatic_partner_selection_allowed"])
        self.assertFalse(summary["app_specific_engine_logic_allowed"])

    def test_segmented_rows_become_typed_stream_and_grouped_plan(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 10, 1.5), (0, 11, 2.5), (1, 20, 0.25)),
            row_schema=("group_ids", "item_ids", "scores"),
            column_roles={
                "group_ids": "group_key",
                "item_ids": "item_id",
                "scores": "score",
            },
            dtypes={"scores": "float64"},
            page_capacity=2,
            stream_id="goal3111_ranked_summary",
            stream_kind="ranked_summary_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="grouped_argmax_f64",
            group_column="group_ids",
            value_columns=("scores",),
            item_column="item_ids",
            user_selected_partner="numba",
        )

        metadata = adapter.to_metadata()
        validation = rt.validate_segmented_typed_stream_adapter(adapter)
        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(metadata["segmented_stream"]["page_count"], 2)
        self.assertEqual(metadata["segmented_stream"]["total_rows"], 3)
        self.assertTrue(metadata["segmented_stream"]["complete_candidate_coverage"])
        self.assertEqual(dict(metadata["status_values"])["row_count"], 3)
        self.assertEqual(dict(metadata["status_values"])["capacity"], 2)
        self.assertFalse(dict(metadata["status_values"])["overflow"])
        self.assertTrue(dict(metadata["status_values"])["complete_candidate_coverage"])
        self.assertEqual(metadata["typed_stream"]["stream_kind"], "ranked_summary_stream")
        self.assertEqual(metadata["continuation_plan"]["operation"], "grouped_argmax_f64")
        self.assertEqual(metadata["continuation_plan"]["user_selected_partner"], "numba")
        self.assertFalse(metadata["device_resident_result_stream_proven"])
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["hidden_dispatch_allowed"])
        self.assertFalse(metadata["release_authorized"])

    def test_adapter_can_record_cuda_buffer_pointers_without_zero_copy_claim(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 10, 1.5),),
            row_schema=("group_ids", "item_ids", "scores"),
            column_roles={
                "group_ids": "group_key",
                "item_ids": "item_id",
                "scores": "score",
            },
            page_capacity=8,
            stream_id="goal3111_cuda_pointer_metadata",
            stream_kind="ranked_summary_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            device_type="cuda",
            data_ptrs={
                "group_ids": 1000,
                "item_ids": 2000,
                "scores": 3000,
                "row_count": 4000,
                "capacity": 5000,
                "overflow": 6000,
                "complete_candidate_coverage": 7000,
            },
            source_protocol="cuda_array_interface",
        )

        metadata = adapter.to_metadata()
        self.assertEqual(metadata["typed_stream"]["device_resident_column_count"], 7)
        self.assertFalse(metadata["device_resident_result_stream_proven"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_adapter_rejects_missing_role_and_auto_partner(self) -> None:
        with self.assertRaisesRegex(ValueError, "column_roles missing"):
            rt.build_segmented_typed_stream_adapter(
                ((0, 1.0),),
                row_schema=("group_ids", "scores"),
                column_roles={"group_ids": "group_key"},
                page_capacity=4,
                stream_id="missing_role",
                stream_kind="grouped_reduction_stream",
                producer_primitive="segmented_row_stream_reference",
                ordering="group_ordered",
            )

        with self.assertRaisesRegex(ValueError, "explicit user partner choice"):
            rt.build_segmented_typed_stream_adapter(
                ((0, 10, 1.5),),
                row_schema=("group_ids", "item_ids", "scores"),
                column_roles={
                    "group_ids": "group_key",
                    "item_ids": "item_id",
                    "scores": "score",
                },
                page_capacity=4,
                stream_id="auto_partner",
                stream_kind="ranked_summary_stream",
                producer_primitive="segmented_row_stream_reference",
                ordering="group_ordered",
                operation="grouped_argmax_f64",
                group_column="group_ids",
                value_columns=("scores",),
                item_column="item_ids",
                user_selected_partner="auto",
            )

    def test_adapter_preserves_segmented_overflow_fail_closed(self) -> None:
        with self.assertRaises(rt.SegmentedRowStreamOverflowError):
            rt.build_segmented_typed_stream_adapter(
                ((0, 10), (1, 20), (2, 30)),
                row_schema=("group_ids", "item_ids"),
                column_roles={"group_ids": "group_key", "item_ids": "item_id"},
                page_capacity=2,
                stream_id="overflow",
                stream_kind="candidate_stream",
                producer_primitive="segmented_row_stream_reference",
                ordering="group_ordered",
                total_row_capacity=2,
            )

    def test_reference_consumer_executes_grouped_argmax_oracle(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 10, 1.5), (0, 11, 2.5), (1, 20, 0.25)),
            row_schema=("group_ids", "item_ids", "scores"),
            column_roles={
                "group_ids": "group_key",
                "item_ids": "item_id",
                "scores": "score",
            },
            page_capacity=2,
            stream_id="goal3111_reference_argmax",
            stream_kind="ranked_summary_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="grouped_argmax_f64",
            group_column="group_ids",
            value_columns=("scores",),
            item_column="item_ids",
            user_selected_partner="numba",
        )

        result = rt.execute_segmented_typed_stream_reference_continuation(adapter)

        self.assertEqual(result["status"], "completed_reference_consumer")
        self.assertEqual(result["operation"], "grouped_argmax_f64")
        self.assertEqual(result["reference_partner"], "python_reference")
        self.assertEqual(result["outputs"]["group_ids"], [0, 1])
        self.assertEqual(result["outputs"]["item_ids"], [11, 20])
        self.assertEqual(result["outputs"]["scores"], [2.5, 0.25])
        self.assertFalse(result["partner_consumer_promoted"])
        self.assertFalse(result["device_resident_result_stream_proven"])
        self.assertFalse(result["true_zero_copy_claim_authorized"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["automatic_partner_selection_allowed"])

    def test_reference_consumer_executes_segmented_sum_oracle(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 1.5), (0, 2.5), (1, 10.0)),
            row_schema=("group_ids", "values"),
            column_roles={"group_ids": "group_key", "values": "score"},
            page_capacity=2,
            stream_id="goal3111_reference_sum",
            stream_kind="grouped_reduction_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="segmented_sum_f64",
            group_column="group_ids",
            value_columns=("values",),
            user_selected_partner="numba",
        )

        result = rt.execute_segmented_typed_stream_reference_continuation(adapter)

        self.assertEqual(result["outputs"]["sums"], [4.0, 10.0])
        self.assertFalse(result["public_speedup_claim_authorized"])
        self.assertFalse(result["rt_core_speedup_claim_authorized"])

    def test_reference_consumer_requires_k_for_topk(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 10, 1.5), (0, 11, 2.5)),
            row_schema=("group_ids", "item_ids", "scores"),
            column_roles={
                "group_ids": "group_key",
                "item_ids": "item_id",
                "scores": "score",
            },
            page_capacity=2,
            stream_id="goal3111_reference_topk",
            stream_kind="ranked_summary_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="grouped_topk_f64",
            group_column="group_ids",
            value_columns=("scores",),
            item_column="item_ids",
            user_selected_partner="numba",
        )

        with self.assertRaisesRegex(ValueError, "k is required"):
            rt.execute_segmented_typed_stream_reference_continuation(adapter)

        result = rt.execute_segmented_typed_stream_reference_continuation(adapter, k=1)
        self.assertEqual(result["outputs"]["group_ids"], [0])
        self.assertEqual(result["outputs"]["item_ids"], [10])
        self.assertEqual(result["outputs"]["scores"], [1.5])

    def test_partner_consumer_dry_run_maps_explicit_partner_columns(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 10, 1.5), (0, 11, 2.5), (1, 20, 0.25)),
            row_schema=("group_ids", "item_ids", "scores"),
            column_roles={
                "group_ids": "group_key",
                "item_ids": "item_id",
                "scores": "score",
            },
            page_capacity=2,
            stream_id="goal3117_partner_argmax",
            stream_kind="ranked_summary_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="grouped_argmax_f64",
            group_column="group_ids",
            value_columns=("scores",),
            item_column="item_ids",
            user_selected_partner="numba",
        )

        request = rt.execute_segmented_typed_stream_partner_continuation(
            adapter,
            partner="numba",
            dry_run=True,
        )

        self.assertEqual(request["status"], "dry_run_partner_consumer_request")
        self.assertEqual(request["consumer_status"], rt.V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_STATUS)
        self.assertEqual(request["operation"], "grouped_argmax_f64")
        self.assertEqual(request["partner"], "numba")
        self.assertTrue(request["supported_operation"])
        self.assertTrue(request["requires_caller_supplied_partner_columns"])
        self.assertEqual(
            request["input_column_mapping"],
            (("group_ids", "group_ids"), ("item_ids", "item_ids"), ("scores", "scores")),
        )
        self.assertFalse(request["automatic_partner_selection_allowed"])
        self.assertFalse(request["hidden_dispatch_allowed"])
        self.assertFalse(request["true_zero_copy_claim_authorized"])
        self.assertFalse(request["release_authorized"])

    def test_partner_consumer_rejects_hidden_materialization_and_auto_partner(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 10, 1.5),),
            row_schema=("group_ids", "item_ids", "scores"),
            column_roles={
                "group_ids": "group_key",
                "item_ids": "item_id",
                "scores": "score",
            },
            page_capacity=2,
            stream_id="goal3117_no_hidden_materialization",
            stream_kind="ranked_summary_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="grouped_argmax_f64",
            group_column="group_ids",
            value_columns=("scores",),
            item_column="item_ids",
            user_selected_partner="numba",
        )

        with self.assertRaisesRegex(ValueError, "explicit partner"):
            rt.plan_segmented_typed_stream_partner_continuation(adapter, partner="auto")
        with self.assertRaisesRegex(ValueError, "partner_columns are required"):
            rt.execute_segmented_typed_stream_partner_continuation(adapter, partner="numba")

    def test_partner_consumer_wraps_scalar_reduction_outputs_in_named_columns(self) -> None:
        count_adapter = rt.build_segmented_typed_stream_adapter(
            ((0,), (0,), (1,)),
            row_schema=("group_ids",),
            column_roles={"group_ids": "group_key"},
            page_capacity=2,
            stream_id="goal3123_named_count",
            stream_kind="grouped_reduction_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="segmented_count_i64",
            group_column="group_ids",
            user_selected_partner="cupy",
        )
        with mock.patch("rtdsl.partner_adapters.partner_group_count_by_key", return_value=[2, 1]) as mocked:
            result = rt.execute_segmented_typed_stream_partner_continuation(
                count_adapter,
                partner="cupy",
                partner_columns={"group_ids": [0, 0, 1]},
            )
        self.assertEqual(result["outputs"], {"counts": [2, 1]})
        mocked.assert_called_once()

        sum_adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 1.5), (0, 2.5), (1, 10.0)),
            row_schema=("group_ids", "values"),
            column_roles={"group_ids": "group_key", "values": "score"},
            page_capacity=2,
            stream_id="goal3123_named_sum",
            stream_kind="grouped_reduction_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="segmented_sum_f64",
            group_column="group_ids",
            value_columns=("values",),
            user_selected_partner="cupy",
        )
        with mock.patch("rtdsl.partner_adapters.partner_group_sum_by_key", return_value=[4.0, 10.0]) as mocked:
            result = rt.execute_segmented_typed_stream_partner_continuation(
                sum_adapter,
                partner="cupy",
                partner_columns={"group_ids": [0, 0, 1], "values": [1.5, 2.5, 10.0]},
            )
        self.assertEqual(result["outputs"], {"sums": [4.0, 10.0]})
        mocked.assert_called_once()

    def test_partner_consumer_dry_run_marks_unsupported_operation(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 10, 1),),
            row_schema=("group_ids", "values", "mask"),
            column_roles={
                "group_ids": "group_key",
                "values": "item_id",
                "mask": "mask",
            },
            page_capacity=2,
            stream_id="goal3117_compact_mask",
            stream_kind="grouped_reduction_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="compact_mask_i64",
            group_column="group_ids",
            value_columns=("values", "mask"),
            user_selected_partner="numba",
        )

        request = rt.execute_segmented_typed_stream_partner_continuation(
            adapter,
            partner="numba",
            dry_run=True,
        )

        self.assertFalse(request["supported_operation"])
        self.assertIn("grouped_argmax_f64", request["supported_operations"])
        self.assertNotIn("compact_mask_i64", request["supported_operations"])

    def test_report_documents_reference_adapter_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("segmented row stream into a typed result stream", text)
        self.assertIn("host_reference_contract_adapter", text)
        self.assertIn("not a native producer", text)
        self.assertIn("not a partner consumer promotion", text)
        self.assertIn("not a true-zero-copy claim", text)
        self.assertIn("not a release authorization", text)
        self.assertIn("not a public speedup claim", text)
        self.assertIn("reference grouped-continuation consumer", text)
        self.assertIn("explicit partner-consumer front door", text)


if __name__ == "__main__":
    unittest.main()
