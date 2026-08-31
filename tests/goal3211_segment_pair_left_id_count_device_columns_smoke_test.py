from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3211_segment_pair_left_id_count_device_columns_smoke_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3211_segment_pair_left_id_count_device_columns_smoke_2026-06-03.md"


class Goal3211SegmentPairLeftIdCountDeviceColumnsSmokeTest(unittest.TestCase):
    def test_artifact_records_live_dense_count_smoke(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3211)
        self.assertEqual(data["commit"], "b9b8df8f")
        self.assertEqual(data["symbol"], "rtdl_optix_prepared_segment_pair_left_id_count_device_columns")
        self.assertEqual(data["left_count"], 16)
        self.assertEqual(data["right_count"], 4)
        self.assertEqual(data["expected_candidate_count"], 64)
        self.assertTrue(data["all_match_expected_counts"])
        self.assertEqual(data["counts"], [4] * 16)

        dense = data["dense_metadata"]
        self.assertEqual(dense["native_symbol"], data["symbol"])
        self.assertTrue(dense["device_resident"])
        self.assertEqual(dense["source_row_count"], 64)
        self.assertEqual(dense["group_capacity"], 16)
        self.assertEqual(
            dense["group_key_semantics"],
            "dense output uses direct-address array index as the implicit group key",
        )
        self.assertFalse(dense["true_zero_copy_authorized"])
        self.assertFalse(dense["release_authorized"])

        negative = data["negative_probe"]
        self.assertTrue(negative["overflow"])
        self.assertFalse(negative["device_resident"])
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

    def test_report_records_scope_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "generic fused count",
            "primitive:",
            "RayJoin-specific native",
            "kernel",
            "source_row_count: 64",
            "all_match_expected_counts: true",
            "overflow: true",
            "device_resident: false",
            "direct-address array index as the implicit group key",
            "public_speedup_claim_authorized: False",
            "true_zero_copy_claim_authorized: False",
            "rayjoin_paper_reproduction_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
