import unittest
from unittest.mock import patch
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rtdsl.baseline_runner import DatasetCase


class _FakePackedPoints:
    count = 2
    dimension = 2


class _FakePreparedPointColumns:
    count = 2
    closed = False

    def to_metadata(self):
        return {
            "schema": "rtdl.optix.prepared_point_probe_columns_2d.v1",
            "point_count": 2,
            "dimension": 2,
            "device_resident_after_prepare": True,
            "true_zero_copy_claim_authorized": False,
        }

    def close(self):
        self.closed = True


class _FakeExactPreparedPointsExecutor:
    closed = False

    def run(self):
        return 7

    def to_metadata(self):
        return {
            "schema": "rtdl.optix.exact_prepared_points_scalar_count_executor_2d.v1",
            "reusable_native_executor": True,
            "row_stream_materialized": False,
            "exact_host_refined_scalar_count": True,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
        }

    def close(self):
        self.closed = True


class _FakeRelationStatusCorrectedExecutor:
    closed = False

    def run(self):
        return {
            "row_count": 7,
            "candidate_row_count": 8,
            "boundary_candidate_row_count": 1,
            "dropped_candidate_row_count": 1,
            "row_stream_materialized": False,
            "boundary_candidate_row_stream_materialized": False,
            "native_exact_device_scalar_count_produced": True,
            "relation_status_correction_used": True,
            "reusable_native_executor_used": True,
            "traversal_seconds": 0.0025,
        }

    def to_metadata(self):
        return {
            "schema": "rtdl.optix.relation_status_corrected_scalar_count_executor_2d.v1",
            "reusable_native_executor": True,
            "row_stream_materialized": False,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
        }

    def close(self):
        self.closed = True


class _FakePolygonRef:
    def __init__(self, value: int) -> None:
        self.id = value


class _FakePackedPolygons:
    polygon_count = 2
    refs = (_FakePolygonRef(0), _FakePolygonRef(1))


class _FakePreparedLeftSet:
    closed = False

    def close(self):
        self.closed = True


class _FakeShapePairActiveCountExecutor:
    closed = False

    def run(self):
        return 3

    def to_metadata(self):
        return {
            "schema": "rtdl.optix.shape_pair_relation_active_count_prepared_left_executor.v1",
            "native_run_symbol": "rtdl_optix_run_shape_pair_relation_active_device_prepared_left_executor",
            "reusable_native_executor": True,
            "row_stream_materialized": False,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
        }

    def close(self):
        self.closed = True


class _FakePreparedShapePairRelation:
    closed = False

    def prepare_active_count_prepared_left_executor(self, _prepared_left):
        return _FakeShapePairActiveCountExecutor()

    def last_phase_timings(self):
        return {
            "mode": "shape_pair_active_count_prepared_left_executor_run",
            "candidate_count_pass": 0.006,
            "containment": 0.007,
            "active_scan": 0.008,
            "count_download": 0.0001,
        }

    def close(self):
        self.closed = True


class _FakePreparedClosedShape:
    closed = False

    def count(self, _packed):
        return 7

    def prepare_point_probe_columns(self, _packed):
        return _FakePreparedPointColumns()

    def count_prepared_points_exact(self, _prepared_points):
        return 7

    def prepare_exact_prepared_points_scalar_count_executor(self, _prepared_points, *, max_candidate_rows=0):
        self.executor_capacity = int(max_candidate_rows)
        return _FakeExactPreparedPointsExecutor()

    def prepare_relation_status_corrected_scalar_count_executor(self, _prepared_points):
        return _FakeRelationStatusCorrectedExecutor()

    def last_phase_timings(self):
        return {
            "mode": "prepared_points_exact_count_executor_run",
            "point_upload": 0.0,
            "candidate_count_pass": 0.0,
            "candidate_write_pass": 0.004,
            "candidate_download": 0.0002,
            "exact_refine": 0.0003,
            "raw_candidate_count": 8,
            "emitted_count": 7,
        }

    def close(self):
        self.closed = True


def _pip_case() -> DatasetCase:
    return DatasetCase(
        workload="pip",
        dataset="fake",
        inputs={"points": ("p0", "p1"), "polygons": ("shape",)},
        note="fake pip",
    )


class V3RebuildSpatialRayJoinRouteTest(unittest.TestCase):
    def test_prepared_optix_suite_uses_prepared_left_for_lsi_count(self):
        from examples.current.research_benchmarks.spatial_rayjoin import (
            rtdl_rayjoin_v2_spatial_join_app as app,
        )

        calls = []

        def fake_workload(workload, **kwargs):
            calls.append((workload, kwargs))
            return {
                "workload": workload,
                "phases_sec": {
                    "prepared_query_sec": 0.001,
                    "prepared_query_sec_total_sec": 0.001,
                },
            }

        with patch.object(app, "run_rayjoin_prepared_optix_workload", side_effect=fake_workload):
            payload = app.run_rayjoin_suite(
                execution_route="prepared_optix",
                result_mode="count",
                include_rows=False,
                query_repeat=1,
                warmup=0,
            )

        self.assertEqual(payload["execution_route"], "prepared_optix")
        by_workload = {workload: kwargs for workload, kwargs in calls}
        self.assertTrue(by_workload["lsi"]["prepare_left_for_count"])
        self.assertFalse(by_workload["pip"]["prepare_left_for_count"])
        self.assertFalse(by_workload["overlay_seed"]["prepare_left_for_count"])

    def test_pip_prepared_points_payload_emits_generic_topology_stream_m3_table(self):
        from examples.current.research_benchmarks.spatial_rayjoin import (
            rtdl_rayjoin_v2_spatial_join_app as app,
        )

        with (
            patch.object(app, "_load_rayjoin_case", return_value=_pip_case()),
            patch("rtdsl.optix_runtime.pack_points", return_value=_FakePackedPoints()),
            patch("rtdsl.optix_runtime.pack_polygons", return_value="packed-shapes"),
            patch(
                "rtdsl.optix_runtime.prepare_point_closed_shape_membership_2d_optix",
                return_value=_FakePreparedClosedShape(),
            ),
        ):
            payload = app.run_rayjoin_prepared_optix_workload(
                "pip",
                result_mode="count",
                count_mode="exact_prepared_points_executor",
                query_repeat=1,
                warmup=0,
            )

        table = payload["topology_stream_m3_phase_table"]
        handle = payload["topology_stream_prepared_handle"]
        self.assertEqual(table["contract"], "topology_stream_m3_phase_table_v1")
        self.assertTrue(table["full_m3_phase_table_complete"])
        self.assertTrue(table["query_stream_resident"])
        self.assertEqual(table["missing_m3_phases_for_public_row"], ())
        self.assertEqual(table["phase_seconds"]["device_transfer_or_residency_sec"], 0.0)
        self.assertEqual(table["phase_seconds"]["rt_traversal_sec"], 0.004)
        self.assertEqual(table["phase_seconds"]["topology_continuation_sec"], 0.0003)
        self.assertFalse(table["public_speedup_claim_authorized"])
        self.assertFalse(table["m7_promotion_authorized"])
        self.assertFalse(table["true_zero_copy_claim_authorized"])

        self.assertEqual(handle["contract"], "topology_stream_prepared_handle_v1")
        self.assertEqual(handle["generic_capability"], "point_location_topology_stream")
        self.assertEqual(
            handle["query_stream_residency"],
            "device_resident_prepared_point_probe_columns_with_reusable_exact_executor",
        )
        self.assertFalse(handle["app_specific_native_engine_logic_allowed"])
        self.assertFalse(handle["release_authorized"])

        self.assertEqual(
            payload["summary"]["output_contract"],
            "point_to_shape_positive_hit_count_exact_prepared_points_executor",
        )
        self.assertTrue(payload["summary"]["exact_prepared_points_executor"]["reusable_native_executor"])
        self.assertEqual(payload["summary"]["exact_prepared_points_executor_capacity"], 14)
        self.assertEqual(
            payload["summary"]["exact_prepared_points_executor_capacity_policy"],
            "auto_max_of_2x_validation_exact_count_and_query_count",
        )

    def test_pip_relation_status_corrected_executor_validated_emits_generic_topology_stream_m3_table(self):
        from examples.current.research_benchmarks.spatial_rayjoin import (
            rtdl_rayjoin_v2_spatial_join_app as app,
        )

        with (
            patch.object(app, "_load_rayjoin_case", return_value=_pip_case()),
            patch("rtdsl.optix_runtime.pack_points", return_value=_FakePackedPoints()),
            patch("rtdsl.optix_runtime.pack_polygons", return_value="packed-shapes"),
            patch(
                "rtdsl.optix_runtime.prepare_point_closed_shape_membership_2d_optix",
                return_value=_FakePreparedClosedShape(),
            ),
        ):
            payload = app.run_rayjoin_prepared_optix_workload(
                "pip",
                result_mode="count",
                count_mode="relation_status_corrected_executor_validated",
                query_repeat=1,
                warmup=0,
            )

        table = payload["topology_stream_m3_phase_table"]
        handle = payload["topology_stream_prepared_handle"]
        native = payload["native_phase_timings"]
        self.assertEqual(payload["row_count"], 7)
        self.assertEqual(
            payload["summary"]["output_contract"],
            "point_to_shape_positive_hit_count_relation_status_corrected_executor_validated",
        )
        self.assertTrue(payload["summary"]["relation_status_corrected_matches_host_exact"])
        self.assertTrue(payload["summary"]["relation_status_corrected_executor_reuses_query_columns"])
        self.assertEqual(native["mode"], "relation_status_corrected_scalar_count_executor_run")
        self.assertTrue(native["native_exact_device_scalar_count_produced"])
        self.assertTrue(native["relation_status_correction_used"])
        self.assertFalse(native["row_stream_materialized"])
        self.assertEqual(table["phase_seconds"]["rt_traversal_sec"], 0.0025)
        self.assertEqual(table["phase_seconds"]["topology_continuation_sec"], 0.0)
        self.assertEqual(table["phase_seconds"]["host_return_or_scalar_materialization_sec"], 0.0)
        self.assertEqual(
            handle["query_stream_residency"],
            "device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor",
        )
        self.assertIn(
            "validated_relation_status_corrected_executor",
            payload["device_resident_continuation_status"],
        )
        self.assertFalse(table["m7_promotion_authorized"])
        self.assertFalse(handle["release_authorized"])

    def test_overlay_active_count_payload_emits_generic_topology_stream_m3_table(self):
        from examples.current.research_benchmarks.spatial_rayjoin import (
            rtdl_rayjoin_v2_spatial_join_app as app,
        )

        with (
            patch(
                "rtdsl.optix_runtime.prepare_shape_pair_relation_flags_optix",
                return_value=_FakePreparedShapePairRelation(),
            ),
            patch("rtdsl.optix_runtime.pack_polygons", return_value=_FakePackedPolygons()),
            patch(
                "rtdsl.optix_runtime.prepare_shape_pair_relation_left_set_optix",
                return_value=_FakePreparedLeftSet(),
            ),
        ):
            with app.prepare_rayjoin_optix_shape_pair_active_count(("right0",)) as prepared:
                packed_left = prepared.pack_left_shapes(("left0", "left1"))
                try:
                    payload = prepared.run_packed_left(
                        packed_left,
                        query_repeat=1,
                        warmup=0,
                    )
                finally:
                    packed_left.close()

        table = payload["topology_stream_m3_phase_table"]
        handle = payload["topology_stream_prepared_handle"]

        self.assertEqual(payload["row_count"], 3)
        self.assertEqual(payload["summary"]["output_contract"], "overlay_active_pair_dependency_count")
        self.assertEqual(table["contract"], "topology_stream_m3_phase_table_v1")
        self.assertTrue(table["full_m3_phase_table_complete"])
        self.assertEqual(table["missing_m3_phases_for_public_row"], ())
        self.assertEqual(table["query_count"], 2)
        self.assertGreater(table["phase_seconds"]["query_stream_prepare_sec"], 0.0)
        self.assertAlmostEqual(table["phase_seconds"]["rt_traversal_sec"], 0.006)
        self.assertAlmostEqual(table["phase_seconds"]["topology_continuation_sec"], 0.015)
        self.assertAlmostEqual(
            table["phase_seconds"]["host_return_or_scalar_materialization_sec"],
            0.0001,
        )
        self.assertFalse(table["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(table["m7_promotion_authorized"])

        self.assertEqual(handle["contract"], "topology_stream_prepared_handle_v1")
        self.assertEqual(handle["generic_capability"], "point_location_topology_stream")
        self.assertEqual(handle["output_contract"], "overlay_active_pair_dependency_count")
        self.assertEqual(
            handle["query_stream_residency"],
            "device_resident_prepared_left_shape_set_with_reusable_active_count_executor",
        )
        self.assertFalse(handle["app_specific_native_engine_logic_allowed"])
        self.assertFalse(handle["release_authorized"])


if __name__ == "__main__":
    unittest.main()
