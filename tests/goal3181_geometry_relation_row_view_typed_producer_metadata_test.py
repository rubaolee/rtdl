from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3181_geometry_relation_row_view_typed_producer_metadata_2026-06-03.md"


class Goal3181GeometryRelationRowViewTypedProducerMetadataTest(unittest.TestCase):
    def test_helper_builds_supported_geometry_relation_streams(self) -> None:
        cases = {
            ("point_id", "shape_id", "membership"): "point_closed_shape_membership_2d",
            ("left_id", "right_id", "intersection_point_x", "intersection_point_y"): "segment_pair_intersection_2d",
            ("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"): "shape_pair_relation_flags_2d",
        }

        for fields, producer in cases.items():
            with self.subTest(fields=fields):
                contract = rt.make_v2_8_geometry_relation_typed_stream_contract(fields, 5)
                metadata = contract.to_metadata()
                validation = rt.validate_typed_result_stream_contract(contract)

                self.assertEqual(validation["status"], "accept", validation)
                self.assertEqual(metadata["stream_kind"], "candidate_stream")
                self.assertEqual(metadata["producer_primitive"], producer)
                self.assertEqual(metadata["column_names"], fields)
                self.assertEqual(metadata["ordering"], "stable_row_order")
                self.assertEqual(metadata["device_resident_column_count"], 0)
                self.assertFalse(metadata["release_authorized"])
                self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_optix_row_view_exposes_typed_metadata_for_relation_rows(self) -> None:
        view = rt.OptixRowView(
            library=object(),
            rows_ptr=None,
            row_count=3,
            row_type=object,
            field_names=("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"),
            _free_on_close=False,
        )
        metadata = view.to_v2_8_typed_result_stream_metadata()
        stream = metadata["typed_result_stream"]
        producer = metadata["v2_8_typed_producer_metadata"]

        self.assertEqual(rt.validate_typed_result_stream_contract(stream)["status"], "accept")
        self.assertEqual(stream["producer_primitive"], "shape_pair_relation_flags_2d")
        self.assertEqual(producer["schema_id"], "shape_pair_relation_flags_2d_rows")
        self.assertEqual(producer["producer_output_residency"], "host_materialized_row_view")
        self.assertFalse(producer["device_resident_output_stream_proven"])
        self.assertFalse(producer["release_authorized"])
        self.assertFalse(producer["public_speedup_claim_authorized"])
        self.assertFalse(producer["rt_core_speedup_claim_authorized"])
        self.assertFalse(producer["true_zero_copy_claim_authorized"])

    def test_unsupported_row_schema_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported v2.8 geometry relation row schema"):
            rt.make_v2_8_geometry_relation_typed_stream_contract(("left_id", "right_id", "score"), 1)

    def test_spatial_rayjoin_gap_row_names_relation_rows_not_ray_triangle_proxy(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("generic 2-D relation-row typed producer metadata", spatial["current_best_path"])
        self.assertIn("prepared shape/segment row views", spatial["current_best_path"])
        self.assertIn("shape-pair active-count route", spatial["current_best_path"])
        self.assertIn("relation-row typed producer metadata now exists", spatial["current_bottleneck"])
        self.assertIn("skips final host row allocation", spatial["current_bottleneck"])
        self.assertIn("device-resident relation-row output", spatial["current_bottleneck"])
        self.assertIn("Goal3181", spatial["evidence_refs"])
        self.assertIn("Goal3183", spatial["evidence_refs"])
        self.assertNotIn("Goal3180", spatial["evidence_refs"])
        self.assertFalse(spatial["release_authorized"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])
        self.assertFalse(spatial["rt_core_speedup_claim_authorized"])
        self.assertFalse(spatial["true_zero_copy_claim_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "point_closed_shape_membership_2d",
            "segment_pair_intersection_2d",
            "shape_pair_relation_flags_2d",
            "host row views",
            "device-resident relation-row output remains future work",
            "`true_zero_copy_claim_authorized: False`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
