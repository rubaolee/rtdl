from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3176_ray_triangle_grouped_i64_typed_producer_metadata_2026-06-03.md"


def _fixture():
    rays = (
        rt.Ray3D(0, 0.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
        rt.Ray3D(1, 2.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
    )
    triangles = (
        rt.Triangle3D(0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
        rt.Triangle3D(1, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0, 0.0),
    )
    return rays, triangles


class Goal3176RayTriangleGroupedI64TypedProducerMetadataTest(unittest.TestCase):
    def test_helper_builds_grouped_reduction_typed_stream(self) -> None:
        contract = rt.make_v2_8_ray_triangle_grouped_i64_reduction_typed_stream_contract(
            3,
            reduction="sum_count",
            data_ptrs={"group_id": 1000, "sum": 2000, "count": 3000},
            device_type="cuda",
            source_protocol="planned_cuda_device_columns",
        )
        metadata = contract.to_metadata()
        validation = rt.validate_typed_result_stream_contract(contract)

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(metadata["stream_kind"], "grouped_reduction_stream")
        self.assertEqual(metadata["producer_primitive"], "ray_triangle_grouped_i64_reduction_3d")
        self.assertEqual(metadata["column_names"], ("group_id", "sum", "count"))
        roles = {column["name"]: column["role"] for column in metadata["columns"]}
        self.assertEqual(roles["group_id"], "group_key")
        self.assertEqual(roles["sum"], "payload")
        self.assertEqual(roles["count"], "payload")
        self.assertEqual(metadata["device_resident_column_count"], 3)
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_cpu_generic_producer_attaches_host_materialized_typed_metadata(self) -> None:
        rays, triangles = _fixture()
        result = rt.run_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
            rays,
            triangles,
            primitive_group_ids=(0, 1),
            primitive_values=(3, 7),
            reduction="sum_count",
            backend="cpu",
        )

        self.assertEqual(result["rows"], ({"group_id": 0, "sum": 3, "count": 1}, {"group_id": 1, "sum": 7, "count": 1}))
        stream = result["typed_result_stream"]
        producer = result["v2_8_typed_producer_metadata"]
        self.assertEqual(stream["stream_kind"], "grouped_reduction_stream")
        self.assertEqual(stream["producer_primitive"], "ray_triangle_grouped_i64_reduction_3d")
        self.assertEqual(stream["column_names"], ("group_id", "sum", "count"))
        self.assertEqual(stream["device_resident_column_count"], 0)
        self.assertEqual(producer["producer_output_residency"], "host_materialized_group_rows")
        self.assertFalse(producer["device_resident_output_stream_proven"])
        self.assertFalse(producer["true_zero_copy_claim_authorized"])
        self.assertFalse(producer["release_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "ray_triangle_grouped_i64_reduction_3d",
            "typed producer metadata",
            "host-materialized",
            "device-resident output remains future work",
            "`true_zero_copy_claim_authorized: False`",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
