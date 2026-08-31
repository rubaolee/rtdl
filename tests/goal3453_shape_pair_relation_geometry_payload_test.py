from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "goal3453_shape_pair_relation_geometry_payload_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3453_shape_pair_relation_geometry_payload_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3453_shape_pair_relation_geometry_payload_pod_2026-06-05.json"


class Goal3453ShapePairRelationGeometryPayloadTest(unittest.TestCase):
    def test_native_struct_and_owner_expose_generic_geometry_payload(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        for phrase in (
            "left_polygon_refs_device_ptr",
            "right_polygon_refs_device_ptr",
            "left_vertices_x_device_ptr",
            "left_vertices_y_device_ptr",
            "right_vertices_x_device_ptr",
            "right_vertices_y_device_ptr",
            "left_bounds_device_ptr",
            "right_bounds_device_ptr",
            "left_polygon_count",
            "right_polygon_count",
            "left_vertex_count",
            "right_vertex_count",
        ):
            self.assertIn(phrase, prelude)
            self.assertIn(phrase, workloads)

        for phrase in (
            "CU_CHECK(cuMemAlloc(&owner->left_polygon_refs",
            "upload(owner->left_polygon_refs",
            "columns_out->right_polygon_refs_device_ptr",
            "prepared->d_right_polygons.ptr",
        ):
            self.assertIn(phrase, workloads)

    def test_python_runtime_wraps_geometry_payload_for_explicit_partner_continuation(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        for phrase in (
            "def as_cupy_geometry_payload_columns(",
            "shape_pair_relation_geometry_payload_device_columns",
            "left_payload_lifetime",
            "right_payload_lifetime",
            "prepared_shape_pair_relation_handle",
            "geometry_payload_device_resident",
            "true_zero_copy_authorized\": False",
        ):
            self.assertIn(phrase, runtime)

    def test_probe_and_report_record_boundary(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3453.shape_pair_relation_geometry_payload.v1",
            "as_cupy_geometry_payload_columns",
            "geometry_payload_matches",
            "metadata_geometry_payload",
            "full_overlay_area_claim_authorized",
        ):
            self.assertIn(phrase, script)

        for phrase in (
            "Goal3453",
            "generic geometry-payload surface",
            "future partner/native witness",
            "does not authorize",
            "bounded generic witness/area continuation",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3453 pod artifact pending")
    def test_pod_artifact_geometry_payload_matches_fixture(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3453.shape_pair_relation_geometry_payload.v1")
        self.assertEqual(payload["goal"], 3453)
        self.assertTrue(payload["geometry_payload_matches"])
        self.assertEqual(payload["observed"], payload["expected"])
        self.assertEqual(payload["metadata_schema_id"], "shape_pair_relation_flags_2d_device_columns")
        self.assertTrue(payload["metadata_geometry_payload"]["device_resident"])
        self.assertEqual(payload["metadata_geometry_payload"]["schema"], "shape_pair_relation_geometry_payload_device_columns")
        self.assertEqual(payload["metadata_geometry_payload"]["left_payload_lifetime"], "relation_column_output_owner")
        self.assertEqual(payload["metadata_geometry_payload"]["right_payload_lifetime"], "prepared_shape_pair_relation_handle")
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
