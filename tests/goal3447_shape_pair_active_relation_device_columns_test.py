from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
TYPED = ROOT / "src" / "rtdsl" / "v2_8_geometry_relation_typed_stream.py"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
SCRIPT = ROOT / "scripts" / "goal3447_shape_pair_active_relation_device_columns_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3447_shape_pair_active_relation_device_columns_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.json"


class Goal3447ShapePairActiveRelationDeviceColumnsTest(unittest.TestCase):
    def test_typed_stream_schema_is_generic_and_non_authorizing(self) -> None:
        fields = (
            "left_id",
            "right_id",
            "requires_segment_intersection",
            "requires_point_containment",
        )
        contract = rt.make_v2_8_geometry_relation_typed_stream_contract(
            fields,
            7,
            device_type="cuda",
            source_protocol="optix_native_shape_pair_relation_flag_device_columns",
            data_ptrs={
                "left_id": 101,
                "right_id": 202,
                "requires_segment_intersection": 303,
                "requires_point_containment": 404,
            },
        )
        metadata = rt.geometry_relation_typed_stream_metadata_for_relation_flag_device_columns(
            row_count=7,
            capacity=16,
            left_ids_device_ptr=101,
            right_ids_device_ptr=202,
            requires_segment_intersection_device_ptr=303,
            requires_point_containment_device_ptr=404,
            device_id=0,
            active_relation_count=7,
            overflow=False,
            native_symbol="rtdl_optix_prepared_shape_pair_relation_active_device_columns",
        )
        stream = contract.to_metadata()
        producer = metadata["v2_8_typed_producer_metadata"]

        self.assertEqual(rt.validate_typed_result_stream_contract(contract)["status"], "accept")
        self.assertEqual(stream["stream_id"], "shape_pair_relation_flags_2d_device_columns")
        self.assertEqual(stream["producer_primitive"], "shape_pair_relation_flags_2d")
        self.assertEqual(producer["schema_id"], "shape_pair_relation_flags_2d_device_columns")
        self.assertEqual(producer["producer_output_residency"], "device_resident_relation_flag_columns")
        self.assertEqual(producer["source_protocol"], "optix_native_shape_pair_relation_flag_device_columns")
        self.assertTrue(producer["device_resident_output_stream_proven"])
        self.assertFalse(producer["release_authorized"])
        self.assertFalse(producer["public_speedup_claim_authorized"])
        self.assertFalse(producer["rt_core_speedup_claim_authorized"])
        self.assertFalse(producer["true_zero_copy_claim_authorized"])
        self.assertFalse(producer["exact_relation_witness_rows_materialized"])
        for old_name in ("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"):
            self.assertNotIn(old_name, producer["column_names"])

    def test_native_surface_compacts_generic_relation_columns(self) -> None:
        native = (
            CORE.read_text(encoding="utf-8")
            + WORKLOADS.read_text(encoding="utf-8")
            + PRELUDE.read_text(encoding="utf-8")
            + API.read_text(encoding="utf-8")
        )
        for phrase in (
            "RtdlNativeShapePairRelationDeviceColumns",
            "shape_pair_relation_active_relation_device_columns_kernel",
            "run_prepared_shape_pair_relation_active_device_columns_optix",
            "rtdl_optix_prepared_shape_pair_relation_active_device_columns",
            "rtdl_optix_release_shape_pair_relation_active_device_columns",
        ):
            self.assertIn(phrase, native)

        workloads = WORKLOADS.read_text(encoding="utf-8")
        native_slice_start = workloads.index(
            "static void run_prepared_shape_pair_relation_active_device_columns_optix"
        )
        native_slice_end = workloads.index(
            "static void release_shape_pair_relation_active_device_columns_optix",
            native_slice_start,
        )
        native_slice = workloads[native_slice_start:native_slice_end].lower()
        for forbidden in ("rayjoin", "cdb", "county", "soil"):
            self.assertNotIn(forbidden, native_slice)

    def test_python_runtime_and_app_expose_resident_relation_column_path(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        typed = TYPED.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "OPTIX_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_COLUMNS_SYMBOL",
            "OPTIX_RELEASE_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_COLUMNS_SYMBOL",
            "class _RtdlNativeShapePairRelationDeviceColumns",
            "class OptixShapePairRelationDeviceColumnOutput",
            "def active_relation_device_columns(",
            '4: "active_relation_device_columns"',
            "geometry_relation_typed_stream_metadata_for_relation_flag_device_columns",
        ):
            self.assertIn(phrase, runtime)
        self.assertIn("V2_8_GEOMETRY_RELATION_DEVICE_RELATION_FLAG_COLUMN_STATUS", typed)
        self.assertIn("def run_packed_left_active_relation_device_columns(", app)
        self.assertIn("prepared_optix_shape_pair_active_relation_device_columns_reuse", app)
        self.assertIn("rtdl.goal3447.shape_pair_active_relation_device_columns.v1", script)
        self.assertIn("all_counts_match", script)

    def test_report_records_boundary_and_next_step(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3447",
            "device-column stream",
            "fail-closed",
            "does not authorize",
            "RayJoin paper reproduction claims",
            "full overlay relation-row",
            "next useful step",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3447 pod artifact pending")
    def test_pod_artifact_counts_match_and_flags_are_closed(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3447.shape_pair_active_relation_device_columns.v1")
        self.assertEqual(payload["goal"], 3447)
        self.assertTrue(payload["all_counts_match"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))
        self.assertEqual(payload["host_counts"], payload["scalar_device_counts"])
        self.assertEqual(payload["host_counts"], payload["column_counts"])
        self.assertGreater(payload["column_speedup_vs_host"]["median"], 1.0)
        for run in payload["runs"]:
            self.assertTrue(run["counts_match"])
            self.assertEqual(
                run["column_native_phase_timings"]["mode"],
                "active_relation_device_columns",
            )
            self.assertTrue(all(value is False for value in run["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
