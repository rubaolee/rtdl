from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_SOURCE = ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
PROBE_SOURCE = ROOT / "scripts" / "goal3147_compact_mask_front_door_pod_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3147_compact_mask_front_door_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3147_pod_artifacts" / "compact_mask_front_door_pod_probe_2026-06-03.json"


class Goal3147CompactMaskFrontDoorTest(unittest.TestCase):
    def test_compact_mask_is_supported_and_deferred_map_is_empty(self) -> None:
        summary = rt.v2_8_segmented_typed_stream_adapter_summary()

        self.assertIn("compact_mask_i64", summary["partner_consumer_supported_operations"])
        self.assertNotIn("compact_mask_i64", summary["partner_consumer_deferred_operations"])
        self.assertEqual(summary["partner_consumer_deferred_operations"], {})
        self.assertFalse(summary["partner_consumer_promoted"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["automatic_partner_selection_allowed"])

    def test_source_uses_generic_compact_mask_front_door(self) -> None:
        adapter = ADAPTER_SOURCE.read_text(encoding="utf-8")
        probe = PROBE_SOURCE.read_text(encoding="utf-8")

        for phrase in (
            '"compact_mask_i64"',
            "run_numba_compact_mask_i64",
            "partner_mask_indices",
            "partner_take_columns_by_indices",
            "canonical_output_schema",
            "stable_input_order",
            "host_prefix_sum_used",
        ):
            self.assertIn(phrase, adapter)
        for phrase in (
            "--warmup-rows",
            "execute_segmented_typed_stream_partner_continuation",
            "values_match_reference",
            "indices_match_reference",
            "true_zero_copy_claim_authorized",
        ):
            self.assertIn(phrase, probe)

    def test_reference_compact_mask_shape(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 10, True), (0, 11, False), (1, 12, True)),
            row_schema=("group_ids", "values", "mask"),
            column_roles={"group_ids": "group_key", "values": "item_id", "mask": "mask"},
            page_capacity=2,
            stream_id="goal3147_reference_compact",
            stream_kind="candidate_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="stable_row_order",
            operation="compact_mask_i64",
            group_column="group_ids",
            value_columns=("values", "mask"),
            user_selected_partner="numba",
        )

        result = rt.execute_segmented_typed_stream_reference_continuation(adapter)
        self.assertEqual(result["outputs"], {"values": [10, 12], "original_indices": [0, 2]})

    def test_report_and_artifact_keep_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "stable row-filter continuation",
            "run_numba_compact_mask_i64",
            "explicit warmup",
            "host_prefix_sum_used: true",
            "does not authorize public speedup",
            "NVIDIA RTX 4000 Ada",
        ):
            self.assertIn(phrase, text)

        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal3147")
        self.assertTrue(artifact["all_match"])
        self.assertEqual(artifact["gpu"], "NVIDIA RTX 4000 Ada Generation")
        for value in artifact["claim_boundary"].values():
            self.assertFalse(value)
        self.assertEqual({row["row_count"] for row in artifact["rows"]}, {1_000_000, 4_000_000})
        for row in artifact["rows"]:
            self.assertTrue(row["values_match_reference"])
            self.assertTrue(row["indices_match_reference"])
            self.assertTrue(row["stable_input_order"])
            self.assertTrue(row["host_prefix_sum_used"])
            self.assertEqual(row["canonical_output_schema"], ["values", "original_indices"])
            self.assertFalse(row["partner_consumer_promoted"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
