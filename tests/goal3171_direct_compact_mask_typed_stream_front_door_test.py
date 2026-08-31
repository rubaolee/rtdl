from __future__ import annotations

from pathlib import Path
from unittest import mock
import unittest

import numpy as np

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
RAYJOIN_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
TRIANGLE_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal3171_direct_compact_mask_typed_stream_front_door_2026-06-03.md"


class Goal3171DirectCompactMaskTypedStreamFrontDoorTest(unittest.TestCase):
    def test_direct_compact_mask_helper_is_exported_and_schema_only_grouped(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("def execute_compact_mask_typed_stream_partner_columns", adapter)
        self.assertTrue(hasattr(rt, "execute_compact_mask_typed_stream_partner_columns"))

        request = rt.execute_compact_mask_typed_stream_partner_columns(
            values=np.asarray([10, 11, 12], dtype=np.int64),
            mask=np.asarray([True, False, True], dtype=np.bool_),
            partner="numba",
            stream_id="goal3171_dry_run",
            dry_run=True,
        )
        self.assertEqual(request["status"], "dry_run_partner_consumer_request")
        self.assertEqual(request["typed_stream"]["stream_kind"], "candidate_stream")
        self.assertEqual(request["continuation_plan"]["operation"], "compact_mask_i64")
        self.assertEqual(request["continuation_plan"]["continuation_semantics"], "filter int64 values by a boolean mask while preserving stable input order")
        self.assertEqual(request["input_column_mapping"], (("values", "values"), ("mask", "mask")))
        self.assertTrue(request["schema_only_group_column"])
        columns = {column["name"]: column for column in request["typed_stream"]["columns"]}
        self.assertEqual(columns["group_ids"]["role"], "group_key")
        self.assertEqual(columns["group_ids"]["shape"], (0,))
        self.assertFalse(columns["group_ids"]["required_for_continuation"])
        self.assertEqual(columns["values"]["role"], "item_id")
        self.assertEqual(columns["mask"]["role"], "mask")
        self.assertEqual(request["source_materialization"], "caller_supplied_partner_columns_no_hidden_host_rows")
        self.assertFalse(request["automatic_partner_selection_allowed"])
        self.assertFalse(request["release_authorized"])
        self.assertFalse(request["true_zero_copy_claim_authorized"])

    def test_direct_compact_mask_helper_preserves_block_size(self) -> None:
        fake_result = {
            "status": "completed",
            "outputs": {"values": (10, 12), "original_indices": (0, 2)},
            "stable_input_order": True,
            "host_prefix_sum_used": True,
            "phase_timing": {"phases_sec": {"partner_continuation": 0.001}},
        }
        with mock.patch(
            "rtdsl.numba_partner_continuation.run_numba_compact_mask_i64",
            return_value=fake_result,
        ) as compact:
            result = rt.execute_compact_mask_typed_stream_partner_columns(
                values=(10, 11, 12),
                mask=(True, False, True),
                partner="numba",
                stream_id="goal3171_execute",
                block_size=384,
            )

        compact.assert_called_once()
        self.assertEqual(compact.call_args.kwargs["block_size"], 384)
        self.assertEqual(result["outputs"]["values"], (10, 12))
        self.assertEqual(result["outputs"]["original_indices"], (0, 2))
        self.assertEqual(result["partner_metadata"]["block_size"], 384)
        self.assertFalse(result["release_authorized"])

    def test_rayjoin_and_triangle_use_direct_helper_without_raw_numba_call(self) -> None:
        for source_path in (RAYJOIN_APP, TRIANGLE_APP):
            with self.subTest(path=source_path.name):
                source = source_path.read_text(encoding="utf-8")
                self.assertIn("execute_compact_mask_typed_stream_partner_columns", source)
                self.assertNotIn("build_segmented_typed_stream_adapter", source)
                self.assertNotIn("execute_segmented_typed_stream_partner_continuation", source)
                self.assertNotIn("rt.run_numba_compact_mask_i64(", source)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "execute_compact_mask_typed_stream_partner_columns",
            "schema-only group column",
            "RayJoin",
            "triangle-counting",
            "`automatic_partner_selection_allowed: False`",
            "does not promote a native producer",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
