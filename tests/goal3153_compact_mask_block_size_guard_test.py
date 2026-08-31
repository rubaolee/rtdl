from __future__ import annotations

from pathlib import Path
from unittest import mock
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_SOURCE = ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
REPORT = ROOT / "docs" / "reports" / "goal3153_compact_mask_block_size_guard_2026-06-03.md"


def _schema_only_compact_mask_adapter():
    return rt.build_segmented_typed_stream_adapter(
        (),
        row_schema=("group_ids", "values", "mask"),
        column_roles={"group_ids": "group_key", "values": "item_id", "mask": "mask"},
        page_capacity=1,
        stream_id="goal3153_compact_mask_schema",
        stream_kind="candidate_stream",
        producer_primitive="schema_only_test_stream",
        ordering="stable_row_order",
        operation="compact_mask_i64",
        group_column="group_ids",
        value_columns=("values", "mask"),
        user_selected_partner="numba",
    )


class Goal3153CompactMaskBlockSizeGuardTest(unittest.TestCase):
    def test_adapter_source_has_generic_positive_guard(self) -> None:
        source = ADAPTER_SOURCE.read_text(encoding="utf-8")

        self.assertIn("def _resolve_compact_mask_block_size", source)
        self.assertIn("block_size must be positive for compact_mask_i64", source)
        self.assertIn("run_numba_compact_mask_i64(values, mask, block_size=resolved_block_size)", source)

    def test_nonpositive_block_size_fails_before_lower_primitive(self) -> None:
        adapter = _schema_only_compact_mask_adapter()

        for block_size in (0, -1):
            with self.subTest(block_size=block_size):
                with mock.patch(
                    "rtdsl.numba_partner_continuation.run_numba_compact_mask_i64"
                ) as compact:
                    with self.assertRaisesRegex(
                        ValueError,
                        "block_size must be positive for compact_mask_i64",
                    ):
                        rt.execute_segmented_typed_stream_partner_continuation(
                            adapter,
                            partner="numba",
                            partner_columns={"values": (10, 11), "mask": (True, False)},
                            group_count=0,
                            block_size=block_size,
                        )
                    compact.assert_not_called()

    def test_default_block_size_still_resolves_to_legacy_default(self) -> None:
        adapter = _schema_only_compact_mask_adapter()
        fake_result = {
            "status": "completed",
            "outputs": {"values": (10,), "original_indices": (0,)},
            "stable_input_order": True,
            "host_prefix_sum_used": True,
            "phase_timing": {"phases_sec": {"partner_continuation": 0.001}},
        }

        with mock.patch(
            "rtdsl.numba_partner_continuation.run_numba_compact_mask_i64",
            return_value=fake_result,
        ) as compact:
            result = rt.execute_segmented_typed_stream_partner_continuation(
                adapter,
                partner="numba",
                partner_columns={"values": (10, 11), "mask": (True, False)},
                group_count=0,
            )

        self.assertEqual(compact.call_args.kwargs["block_size"], 256)
        self.assertEqual(result["partner_metadata"]["block_size"], 256)
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["public_speedup_claim_authorized"])
        self.assertFalse(result["true_zero_copy_claim_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3153",
            "Goal3152's Claude review",
            "block_size <= 0",
            "release_authorized: False",
            "public_speedup_claim_authorized: False",
            "rt_core_speedup_claim_authorized: False",
            "true_zero_copy_claim_authorized: False",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

