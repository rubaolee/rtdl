from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3189_pair_column_grouped_count_continuation_2026-06-03.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3189_pod_pair_column_grouped_count_continuation_2026-06-03.json"


class Goal3189PairColumnGroupedCountContinuationTest(unittest.TestCase):
    def test_python_front_door_uses_existing_generic_device_column_count(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        start = runtime.index("    def grouped_count_by_left_id(self, *, group_capacity: int)")
        end = runtime.index("    def close(self) -> None:", start)
        body = runtime[start:end]

        self.assertIn("OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL", body)
        self.assertIn("_RtdlDevicePayloadField", body)
        self.assertIn("_DEVICE_PAYLOAD_DTYPE_INT64", body)
        self.assertIn("self.left_ids_device_ptr", body)
        self.assertIn("pair-column left_id axis", body)
        self.assertIn("segment_pair_candidate_left_id_count", body)
        self.assertIn("OptixRowView", body)
        self.assertNotIn("rayjoin", body.lower())
        self.assertNotIn("intersection_point", body)

    def test_grouped_count_fails_closed_on_overflowed_candidate_stream(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        start = runtime.index("    def grouped_count_by_left_id(self, *, group_capacity: int)")
        end = runtime.index("    def close(self) -> None:", start)
        body = runtime[start:end]

        self.assertIn("if self.overflow:", body)
        self.assertIn("cannot group an overflowed segment-pair candidate column stream", body)
        self.assertIn("_raise_on_partner_resident_grouped_capacity_overflow", body)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "generic device-column grouped-count continuation",
            "counts candidate rows per `left_id`",
            "does not add a new native kernel",
            "host-materialized compact count rows",
            "direct-address key capacity",
            "all_match_exact_rows: true",
            "true_zero_copy_claim_authorized: False",
            "release_authorized: False",
        ):
            self.assertIn(phrase, report)

    def test_pod_artifact_records_live_grouped_count_evidence(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3189)
        self.assertEqual(data["focused_unittest_slice"]["status"], "passed")
        self.assertTrue(data["live_smoke"]["all_match_exact_rows"])
        self.assertEqual(data["live_smoke"]["exact_row_count"], 64)
        self.assertEqual(data["live_smoke"]["candidate_columns"]["row_count"], 64)
        self.assertEqual(data["live_smoke"]["candidate_columns"]["candidate_event_count"], 64)
        self.assertEqual(data["live_smoke"]["group_capacity"], 300)
        self.assertEqual(
            data["live_smoke"]["group_capacity_semantics"],
            "direct-address key capacity; must exceed max non-negative left_id",
        )
        self.assertFalse(data["live_smoke"]["candidate_columns"]["overflow"])
        self.assertFalse(data["live_smoke"]["grouped_count_result_device_resident"])
        self.assertEqual(
            data["negative_probe"]["group_capacity_64_status"],
            "failed_closed_on_left_id_key_range",
        )
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_specific_native_logic_added"])


if __name__ == "__main__":
    unittest.main()
