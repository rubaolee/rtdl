from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3189_pair_column_grouped_count_continuation_2026-06-03.md"


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
            "true_zero_copy_claim_authorized: False",
            "release_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
