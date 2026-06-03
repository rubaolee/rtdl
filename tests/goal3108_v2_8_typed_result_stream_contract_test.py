from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3108_v2_8_typed_result_stream_contract_2026-06-03.md"


def _sample_stream() -> rt.V28TypedResultStreamContract:
    columns = (
        rt.typed_result_column(
            "group_ids",
            "group_key",
            "int64",
            (8,),
            device_type="cuda",
            data_ptr=1000,
            source_protocol="cuda_array_interface",
        ),
        rt.typed_result_column(
            "item_ids",
            "item_id",
            "int64",
            (8,),
            device_type="cuda",
            data_ptr=2000,
            source_protocol="cuda_array_interface",
        ),
        rt.typed_result_column(
            "scores",
            "score",
            "float64",
            (8,),
            device_type="cuda",
            data_ptr=3000,
            source_protocol="cuda_array_interface",
        ),
    )
    status_columns = rt.typed_result_status_columns(
        device_type="cuda",
        row_count_ptr=4000,
        capacity_ptr=5000,
        overflow_ptr=6000,
        complete_ptr=7000,
        source_protocol="cuda_array_interface",
    )
    return rt.make_typed_result_stream_contract(
        stream_id="goal3108_sample_ranked_summary",
        stream_kind="ranked_summary_stream",
        producer_primitive="fixed_radius_ranked_summary",
        columns=columns,
        status_columns=status_columns,
        ordering="group_ordered",
        page_capacity=1024,
    )


class Goal3108V28TypedResultStreamContractTest(unittest.TestCase):
    def test_contract_summary_is_internal_and_non_authorizing(self) -> None:
        summary = rt.v2_8_typed_result_stream_contract_summary()

        self.assertEqual(summary["contract_version"], rt.V2_8_TYPED_RESULT_STREAM_VERSION)
        self.assertEqual(summary["target"], rt.V2_8_FIRST_RUNTIME_TARGET)
        self.assertIn("ranked_summary_stream", summary["stream_kinds"])
        self.assertIn("grouped_argmax_f64", summary["allowed_continuations"])
        self.assertEqual(summary["segmented_page_failure_mode"], "fail_closed_overflow")
        self.assertFalse(summary["native_engine_app_specific_logic_allowed"])
        self.assertFalse(summary["automatic_partner_selection_allowed"])
        self.assertFalse(summary["hidden_dispatch_allowed"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["rt_core_speedup_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])

    def test_valid_stream_uses_typed_device_columns_and_status_columns(self) -> None:
        stream = _sample_stream()
        metadata = stream.to_metadata()
        validation = rt.validate_typed_result_stream_contract(stream)

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(metadata["device_resident_column_count"], 7)
        self.assertEqual(tuple(metadata["status_column_names"]), rt.V2_8_TYPED_RESULT_STREAM_STATUS_COLUMNS)
        self.assertEqual(metadata["segmented_page_failure_mode"], "fail_closed_overflow")
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["hidden_dispatch_allowed"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_grouped_continuation_requires_user_selected_partner(self) -> None:
        stream = _sample_stream()
        plan = rt.plan_grouped_continuation_for_typed_result_stream(
            stream,
            operation="grouped_argmax_f64",
            group_column="group_ids",
            value_columns=("scores",),
            item_column="item_ids",
            user_selected_partner="numba",
        )

        metadata = plan.to_metadata()
        validation = rt.validate_grouped_continuation_plan(plan)
        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(metadata["user_selected_partner"], "numba")
        self.assertEqual(metadata["continuation_status"], "contract_only")
        self.assertEqual(
            metadata["continuation_semantics"],
            rt.V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS["grouped_argmax_f64"],
        )
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["hidden_dispatch_allowed"])
        self.assertFalse(metadata["release_authorized"])

        with self.assertRaises(ValueError):
            rt.plan_grouped_continuation_for_typed_result_stream(
                stream,
                operation="grouped_argmax_f64",
                group_column="group_ids",
                value_columns=("scores",),
                item_column="item_ids",
                user_selected_partner="auto",
            )
        with self.assertRaises(ValueError):
            rt.plan_grouped_continuation_for_typed_result_stream(
                stream,
                operation="grouped_argmax_f64",
                group_column="group_ids",
                value_columns=("scores",),
                item_column="item_ids",
            )

    def test_contract_rejects_missing_status_columns(self) -> None:
        columns = (
            rt.typed_result_column("group_ids", "group_key", "int64", (8,)),
            rt.typed_result_column("scores", "score", "float64", (8,)),
        )

        with self.assertRaisesRegex(ValueError, "missing status column"):
            rt.make_typed_result_stream_contract(
                stream_id="missing_status",
                stream_kind="grouped_reduction_stream",
                producer_primitive="segmented_sum",
                columns=columns,
                status_columns=rt.typed_result_status_columns()[:-1],
                ordering="group_ordered",
                page_capacity=128,
            )

    def test_contract_rejects_unordered_stream_without_row_offset(self) -> None:
        columns = (
            rt.typed_result_column("group_ids", "group_key", "int64", (8,)),
            rt.typed_result_column("scores", "score", "float64", (8,)),
        )

        with self.assertRaisesRegex(ValueError, "row_offset"):
            rt.make_typed_result_stream_contract(
                stream_id="unordered_without_offset",
                stream_kind="grouped_reduction_stream",
                producer_primitive="segmented_sum",
                columns=columns,
                status_columns=rt.typed_result_status_columns(),
                ordering="unordered_with_explicit_sort_key",
                page_capacity=128,
            )

    def test_continuation_rejects_wrong_group_column_role(self) -> None:
        stream = _sample_stream()

        with self.assertRaisesRegex(ValueError, "group_key"):
            rt.plan_grouped_continuation_for_typed_result_stream(
                stream,
                operation="grouped_argmax_f64",
                group_column="scores",
                value_columns=("scores",),
                item_column="item_ids",
                user_selected_partner="numba",
            )

    def test_public_exports_include_contract_surface(self) -> None:
        for name in (
            "V28TypedResultStreamContract",
            "V2_8_TYPED_RESULT_STREAM_TARGET",
            "V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS",
            "make_typed_result_stream_contract",
            "plan_grouped_continuation_for_typed_result_stream",
            "validate_typed_result_stream_contract",
        ):
            with self.subTest(name=name):
                self.assertIn(name, rt.__all__)

    def test_report_documents_scope_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("typed device-resident result streams", text)
        self.assertIn(rt.V2_8_FIRST_RUNTIME_TARGET, text)
        self.assertIn("contract-level slice", text)
        self.assertIn("RtdlBufferDescriptor", text)
        self.assertIn("fail_closed_overflow", text)
        for phrase in (
            "not a native kernel promotion",
            "not a release authorization",
            "not a public speedup claim",
            "not a true-zero-copy claim",
            "not hidden partner selection",
            "not user-defined shader injection",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
