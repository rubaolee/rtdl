from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_SOURCE = ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
PROBE_SOURCE = ROOT / "scripts" / "goal3145_segmented_minmax_front_door_pod_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3145_segmented_minmax_front_door_canonical_compaction_2026-06-03.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3145_pod_artifacts"
    / "segmented_minmax_front_door_pod_probe_2026-06-03.json"
)


class Goal3145SegmentedMinmaxFrontDoorCanonicalCompactionTest(unittest.TestCase):
    def test_adapter_exposes_minmax_as_supported_front_door_operations(self) -> None:
        summary = rt.v2_8_segmented_typed_stream_adapter_summary()

        self.assertIn("segmented_min_f64", summary["partner_consumer_supported_operations"])
        self.assertIn("segmented_max_f64", summary["partner_consumer_supported_operations"])
        self.assertNotIn("segmented_min_f64", summary["partner_consumer_deferred_operations"])
        self.assertNotIn("segmented_max_f64", summary["partner_consumer_deferred_operations"])
        self.assertIn("compact_mask_i64", summary["partner_consumer_deferred_operations"])
        self.assertFalse(summary["partner_consumer_promoted"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["automatic_partner_selection_allowed"])

    def test_source_uses_generic_grouped_primitives_and_canonical_outputs(self) -> None:
        adapter = ADAPTER_SOURCE.read_text(encoding="utf-8")
        probe = PROBE_SOURCE.read_text(encoding="utf-8")

        for phrase in (
            'operation in {"segmented_min_f64", "segmented_max_f64"}',
            "partner_group_count_by_key",
            "partner_group_min_by_key",
            "partner_group_max_by_key",
            "_canonical_segmented_minmax_columns",
            "canonical_output_host_compaction_used",
        ):
            self.assertIn(phrase, adapter)
        for phrase in (
            "execute_segmented_typed_stream_partner_continuation",
            "partner_columns",
            "matches_reference",
            "rt_core_speedup_claim_authorized",
        ):
            self.assertIn(phrase, probe)

    def test_reference_and_partner_contract_return_same_canonical_shape(self) -> None:
        adapter = rt.build_segmented_typed_stream_adapter(
            ((0, 1.5), (0, 2.5), (2, 10.0)),
            row_schema=("group_ids", "values"),
            column_roles={"group_ids": "group_key", "values": "score"},
            page_capacity=2,
            stream_id="goal3145_contract_min",
            stream_kind="grouped_reduction_stream",
            producer_primitive="segmented_row_stream_reference",
            ordering="group_ordered",
            operation="segmented_min_f64",
            group_column="group_ids",
            value_columns=("values",),
            user_selected_partner="numba",
        )

        reference = rt.execute_segmented_typed_stream_reference_continuation(adapter, group_count=3)
        self.assertEqual(reference["outputs"], {"group_ids": [0, 2], "mins": [1.5, 10.0], "missing_group_ids": [1]})

    def test_pod_artifact_and_report_keep_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "segmented_min_f64",
            "segmented_max_f64",
            "canonical_output_host_compaction_used: true",
            "not claim device-resident result streams",
            "NVIDIA RTX 4000 Ada",
        ):
            self.assertIn(phrase, report)

        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal3145")
        self.assertTrue(artifact["all_match"])
        self.assertEqual(artifact["gpu"], "NVIDIA RTX 4000 Ada Generation")
        for value in artifact["claim_boundary"].values():
            self.assertFalse(value)

        operations = {row["operation"] for row in artifact["rows"]}
        self.assertEqual(operations, {"segmented_min_f64", "segmented_max_f64"})
        row_counts = {row["row_count"] for row in artifact["rows"]}
        self.assertEqual(row_counts, {65536, 1048576})
        for row in artifact["rows"]:
            self.assertTrue(row["matches_reference"])
            self.assertTrue(row["canonical_output_host_compaction_used"])
            self.assertFalse(row["partner_consumer_promoted"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
