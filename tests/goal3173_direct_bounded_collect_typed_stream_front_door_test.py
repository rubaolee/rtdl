from __future__ import annotations

from pathlib import Path
from unittest import mock
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
REPORT = ROOT / "docs" / "reports" / "goal3173_direct_bounded_collect_typed_stream_front_door_2026-06-03.md"


class Goal3173DirectBoundedCollectTypedStreamFrontDoorTest(unittest.TestCase):
    def test_direct_bounded_collect_helper_is_exported_and_generic(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("def execute_bounded_collect_typed_stream_partner_columns", adapter)
        self.assertTrue(hasattr(rt, "execute_bounded_collect_typed_stream_partner_columns"))

        request = rt.execute_bounded_collect_typed_stream_partner_columns(
            group_ids=(0, 1, 1, 2),
            item_ids=(10, 20, 21, 30),
            group_count=3,
            k=2,
            partner="torch",
            stream_id="goal3173_dry_run",
            total_row_capacity=6,
            dry_run=True,
        )

        self.assertEqual(request["status"], "dry_run_partner_consumer_request")
        self.assertEqual(request["typed_stream"]["stream_kind"], "bounded_witness_stream")
        self.assertEqual(request["operation"], "bounded_collect_finalize_i64")
        self.assertEqual(
            request["continuation_plan"]["continuation_semantics"],
            rt.V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS["bounded_collect_finalize_i64"],
        )
        self.assertEqual(request["input_column_mapping"], (("group_ids", "group_ids"), ("item_ids", "item_ids")))
        self.assertEqual(request["bounded_collection_failure_mode"], "fail_closed_overflow")
        self.assertEqual(request["canonical_output_schema"], ("group_ids", "item_ids", "row_offsets"))
        self.assertEqual(request["source_materialization"], "caller_supplied_partner_columns_no_hidden_host_rows")
        columns = {column["name"]: column for column in request["typed_stream"]["columns"]}
        self.assertEqual(columns["group_ids"]["role"], "group_key")
        self.assertEqual(columns["item_ids"]["role"], "item_id")
        self.assertFalse(request["automatic_partner_selection_allowed"])
        self.assertFalse(request["release_authorized"])
        self.assertFalse(request["true_zero_copy_claim_authorized"])
        self.assertFalse(request["app_specific_engine_logic_allowed"])

    def test_direct_bounded_collect_rejects_auto_partner_and_bad_k(self) -> None:
        with self.assertRaisesRegex(ValueError, "explicit partner"):
            rt.execute_bounded_collect_typed_stream_partner_columns(
                group_ids=(0,),
                item_ids=(10,),
                group_count=1,
                k=1,
                partner="auto",
                stream_id="goal3173_auto",
                dry_run=True,
            )
        with self.assertRaisesRegex(ValueError, "k must be positive"):
            rt.execute_bounded_collect_typed_stream_partner_columns(
                group_ids=(0,),
                item_ids=(10,),
                group_count=1,
                k=0,
                partner="torch",
                stream_id="goal3173_bad_k",
                dry_run=True,
            )

    def test_direct_bounded_collect_executes_via_existing_partner_front_door(self) -> None:
        fake_result = {
            "columns": {
                "group_ids": ("g0", "g1", "g1", "g2"),
                "item_ids": (10, 20, 21, 30),
                "row_offsets": (0, 1, 3, 4),
            },
            "metadata": {
                "adapter": "bounded_collect_finalize_i64_partner_columns",
                "partner": "torch",
                "operation": "bounded_collect_finalize_i64",
                "failure_mode": "fail_closed_overflow",
            },
        }
        with mock.patch(
            "rtdsl.partner_adapters.bounded_collect_finalize_i64_partner_columns",
            return_value=fake_result,
        ) as bounded:
            result = rt.execute_bounded_collect_typed_stream_partner_columns(
                group_ids=(0, 1, 1, 2),
                item_ids=(10, 20, 21, 30),
                group_count=3,
                k=2,
                partner="torch",
                stream_id="goal3173_execute",
                total_row_capacity=4,
            )

        bounded.assert_called_once()
        self.assertEqual(bounded.call_args.kwargs["group_count"], 3)
        self.assertEqual(bounded.call_args.kwargs["k"], 2)
        self.assertEqual(bounded.call_args.kwargs["total_row_capacity"], 4)
        self.assertEqual(bounded.call_args.kwargs["partner"], "torch")
        self.assertEqual(result["outputs"]["row_offsets"], (0, 1, 3, 4))
        self.assertEqual(result["partner_metadata"]["failure_mode"], "fail_closed_overflow")
        self.assertFalse(result["release_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "execute_bounded_collect_typed_stream_partner_columns",
            "bounded_collect_finalize_i64",
            "fail-closed overflow",
            "caller-supplied partner columns",
            "`automatic_partner_selection_allowed: False`",
            "does not promote a native producer",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
