from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3394_optix_exact_membership_device_columns_bridge_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3394_optix_exact_membership_device_columns_live_probe.py"


class Goal3394OptixExactMembershipDeviceColumnsBridgeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_live_probe_exact_pair_identity(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3394.optix_exact_membership_device_columns_live_probe.v1")
        self.assertEqual(payload["goal"], 3394)
        self.assertEqual(payload["count"], 4096)
        self.assertEqual(payload["point_count"], 4096)
        self.assertEqual(payload["shape_count"], 3762)
        self.assertEqual(payload["exact_row_count"], 11316)
        self.assertEqual(payload["device_column_row_count"], 11316)
        self.assertEqual(payload["candidate_event_count"], 11316)
        self.assertEqual(payload["exact_relation_row_count"], 11316)
        self.assertTrue(payload["device_resident"])
        self.assertFalse(payload["overflow"])
        self.assertTrue(payload["pairs_match_exact_rows"])
        self.assertEqual(payload["missing_exact_pair_count"], 0)
        self.assertEqual(payload["extra_pair_count"], 0)
        self.assertEqual(
            payload["native_symbol"],
            "rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d",
        )
        self.assertIn("exact_device_columns(points)", self.script)

    def test_metadata_labels_exact_host_refined_bridge_not_candidate_stream(self):
        metadata = self.payload["metadata"]
        stream = metadata["typed_result_stream"]
        producer = metadata["v2_8_typed_producer_metadata"]
        runtime = metadata["runtime"]
        self.assertEqual(stream["stream_id"], "point_closed_shape_membership_2d_exact_device_columns")
        self.assertEqual(stream["stream_kind"], "exact_relation_stream")
        self.assertEqual(stream["producer_primitive"], "point_closed_shape_membership_2d_exact_host_refined")
        self.assertEqual(stream["relation_row_count"], 11316)
        self.assertEqual(producer["schema_id"], "point_closed_shape_membership_2d_exact_device_columns")
        self.assertEqual(producer["producer_output_residency"], "device_resident_exact_id_columns")
        self.assertTrue(producer["host_refined_exact_rows_inside_native_bridge"])
        self.assertFalse(producer["device_only_exact_predicate_produced"])
        self.assertEqual(producer["exact_relation_row_count"], 11316)
        self.assertEqual(producer["legacy_pair_column_count_field"], "candidate_event_count")
        self.assertEqual(runtime["output_residency"], "device_resident_exact_id_columns")
        self.assertTrue(runtime["host_refined_exact_rows_inside_native_bridge"])
        self.assertEqual(runtime["relation_row_count"], 11316)

    def test_claim_boundaries_stay_blocked(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        boundary = self.payload["implementation_boundary"]
        self.assertTrue(boundary["host_refined_exact_rows_inside_native_bridge"])
        self.assertTrue(boundary["native_exact_device_row_stream_produced"])
        self.assertFalse(boundary["device_only_exact_predicate_produced"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])
        self.assertIn("does not authorize release", self.report)
        self.assertIn("device-only", self.report)
        self.assertIn("legacy_pair_column_count_field = candidate_event_count", self.report)


if __name__ == "__main__":
    unittest.main()
