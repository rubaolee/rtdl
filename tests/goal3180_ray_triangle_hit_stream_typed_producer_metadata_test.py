from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3180_ray_triangle_hit_stream_typed_producer_metadata_2026-06-03.md"


class Goal3180RayTriangleHitStreamTypedProducerMetadataTest(unittest.TestCase):
    def test_helper_builds_generic_hit_stream_typed_contract(self) -> None:
        contract = rt.make_v2_8_ray_triangle_hit_stream_typed_stream_contract(
            3,
            capacity=8,
            device_type="cuda",
            source_protocol="native_optix_device_columns",
            data_ptrs={"ray_ids": 1000, "primitive_ids": 2000},
            row_count_ptr=3000,
            overflow_ptr=4000,
        )
        metadata = contract.to_metadata()
        validation = rt.validate_typed_result_stream_contract(contract)

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(metadata["stream_kind"], "hit_stream")
        self.assertEqual(metadata["producer_primitive"], rt.V2_8_RAY_TRIANGLE_HIT_STREAM_TYPED_PRODUCER_PRIMITIVE)
        self.assertEqual(metadata["column_names"], ("ray_ids", "primitive_ids"))
        roles = {column["name"]: column["role"] for column in metadata["columns"]}
        self.assertEqual(roles["ray_ids"], "group_key")
        self.assertEqual(roles["primitive_ids"], "item_id")
        self.assertEqual(metadata["ordering"], "event_ordered")
        self.assertEqual(metadata["page_capacity"], 8)
        self.assertEqual(metadata["device_resident_column_count"], 4)
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_native_device_hit_stream_handoff_attaches_v2_8_metadata(self) -> None:
        handoff = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=rt.RtdlRawCudaColumn("ray_ids", "int64", 1000, 3),
            primitive_ids=rt.RtdlRawCudaColumn("primitive_ids", "int64", 2000, 3),
            row_count=3,
            capacity=8,
            overflow=False,
            native_device_column_output_proven_on_hardware=True,
            producer_consumer_stream_ordering="host_synchronized_before_consumer",
            row_count_device_ptr=3000,
            hit_event_count_device_ptr=3500,
            overflow_device_ptr=4000,
        )
        metadata = handoff.to_metadata()
        stream = metadata["typed_result_stream"]
        producer = metadata["v2_8_typed_producer_metadata"]
        validation = rt.validate_typed_result_stream_contract(stream)

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(stream["stream_kind"], "hit_stream")
        self.assertEqual(stream["producer_primitive"], "ray_triangle_hit_stream_3d")
        self.assertEqual(stream["column_names"], ("ray_ids", "primitive_ids"))
        self.assertEqual(stream["device_resident_column_count"], 4)
        self.assertEqual(producer["producer_output_residency"], "native_device_columns")
        self.assertTrue(producer["native_device_column_output_proven_on_hardware"])
        self.assertTrue(producer["device_resident_output_stream_proven"])
        self.assertTrue(producer["device_resident_status_for_partner"])
        self.assertFalse(producer["event_or_same_stream_ordering_proven"])
        self.assertFalse(producer["release_authorized"])
        self.assertFalse(producer["public_speedup_claim_authorized"])
        self.assertFalse(producer["rt_core_speedup_claim_authorized"])
        self.assertFalse(producer["true_zero_copy_claim_authorized"])

    def test_triangle_gap_row_records_hit_stream_metadata_not_completion(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}

        spatial = rows["spatial_rayjoin"]
        self.assertIn("generic 2-D relation-row typed producer metadata", spatial["current_best_path"])
        self.assertIn("relation-row typed producer metadata", spatial["current_bottleneck"])
        self.assertIn("parity/count grouping over resident rows", spatial["current_bottleneck"])
        self.assertNotIn("Goal3180", spatial["evidence_refs"])

        triangle = rows["triangle_counting"]
        self.assertIn("generic ray/triangle hit-stream typed producer metadata", triangle["current_best_path"])
        self.assertIn("generic native typed candidate-row producer metadata now exists", triangle["current_bottleneck"])
        self.assertIn("segmented/streamed graph lowering", triangle["current_bottleneck"])
        self.assertIn("benchmark-app adoption of resident candidate streams", triangle["current_bottleneck"])
        self.assertIn("Goal3180", triangle["evidence_refs"])

        for row in (spatial, triangle):
            self.assertFalse(row["app_specific_engine_logic_allowed"])
            self.assertFalse(row["automatic_partner_selection_allowed"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "ray_triangle_hit_stream_3d",
            "typed producer metadata",
            "Spatial RayJoin",
            "Triangle counting",
            "benchmark-app adoption",
            "`true_zero_copy_claim_authorized: False`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
