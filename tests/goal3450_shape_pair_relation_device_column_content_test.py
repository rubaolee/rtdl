from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3450_shape_pair_relation_device_column_content_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3450_shape_pair_relation_device_column_content_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3450_shape_pair_relation_device_column_content_pod_2026-06-05.json"


class Goal3450ShapePairRelationDeviceColumnContentTest(unittest.TestCase):
    def test_probe_compares_host_and_device_row_content(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3450.shape_pair_relation_device_column_content.v1",
            "goal3450_sparse_id_synthetic_fixture",
            "host_active_rows",
            "device_active_rows",
            "rows_match",
            "_host_active_rows",
            "_device_active_rows",
            "requires_segment_intersection",
            "requires_point_containment",
            "active_relation_device_columns",
        ):
            self.assertIn(phrase, script)

    def test_probe_records_fail_closed_overflow_capacity_path(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "max_rows=1",
            "overflow_capacity_probe",
            "retry_capacity_hint",
            "metadata_capacity_status",
            "active_relation_count",
        ):
            self.assertIn(phrase, script)

    def test_report_records_boundary_and_remaining_work(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3450",
            "content-correctness gap",
            "same active relation ids and dependency flags",
            "does not authorize",
            "RTDL-beats-RayJoin claims",
            "full overlay witnesses",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3450 pod artifact pending")
    def test_pod_artifact_rows_match_and_overflow_fails_closed(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3450.shape_pair_relation_device_column_content.v1")
        self.assertEqual(payload["goal"], 3450)
        self.assertTrue(payload["rows_match"])
        self.assertEqual(payload["host_active_rows"], payload["device_active_rows"])
        self.assertEqual(payload["host_row_count"], payload["device_row_count"])
        self.assertGreater(payload["host_row_count"], 0)
        self.assertEqual(payload["metadata_schema_id"], "shape_pair_relation_flags_2d_device_columns")
        self.assertTrue(payload["metadata_device_resident_output_stream_proven"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))

        overflow = payload["overflow_capacity_probe"]
        self.assertTrue(overflow["overflow"])
        self.assertEqual(overflow["row_count"], 0)
        self.assertEqual(overflow["retry_capacity_hint"], overflow["active_relation_count"])
        self.assertTrue(overflow["metadata_capacity_status"]["overflowed"])
        self.assertFalse(overflow["metadata_capacity_status"]["partial_result_returned"])


if __name__ == "__main__":
    unittest.main()
