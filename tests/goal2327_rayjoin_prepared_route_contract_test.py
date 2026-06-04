from __future__ import annotations

import unittest
from unittest import mock

from rtdsl.baseline_runner import DatasetCase

from examples.v2_0.research_benchmarks.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as app


class _FakeRawView:
    def __init__(self, row_count: int):
        self.row_count = row_count
        self.closed = False

    def to_dict_rows(self):
        return tuple({"id": index} for index in range(self.row_count))

    def close(self) -> None:
        self.closed = True


class _FakePackedPoints:
    count = 1
    dimension = 2


class _FakeGroupedCountColumns:
    def __init__(self, source_row_count: int):
        self.source_row_count = source_row_count
        self.overflow = False
        self.closed = False

    def to_metadata(self):
        return {
            "output_residency": "device_resident_dense_grouped_count_column",
            "source_row_count": self.source_row_count,
        }

    def close(self) -> None:
        self.closed = True


class _FakeBoundaryEventColumns:
    def __init__(self, row_count: int):
        self.row_count = row_count
        self.overflow = False
        self.closed = False
        self.group_capacity: int | None = None

    def grouped_count_by_point_id_device_columns(self, *, group_capacity: int):
        self.group_capacity = int(group_capacity)
        return _FakeGroupedCountColumns(self.row_count)

    def to_metadata(self):
        return {
            "runtime": {
                "output_residency": "device_resident_boundary_event_columns",
                "row_count": self.row_count,
            }
        }

    def close(self) -> None:
        self.closed = True


class _FakePrepared:
    def __init__(self, row_count: int):
        self.row_count = row_count
        self.closed = False

    def count(self, _packed):
        return self.row_count

    def count_device_filtered(self, _packed):
        return self.row_count

    def count_active(self, _packed):
        return self.row_count

    def run_raw(self, _packed, **_kwargs):
        return _FakeRawView(self.row_count)

    def first_boundary_crossing_device_columns(self, _packed, *, max_rows: int | None = None):
        return _FakeBoundaryEventColumns(min(self.row_count, int(max_rows or self.row_count)))

    def last_phase_timings(self):
        return {
            "native_query_sec": 0.001,
            "candidate_count": self.row_count,
        }

    def close(self) -> None:
        self.closed = True


def _case(workload: str) -> DatasetCase:
    if workload == "overlay_seed":
        return DatasetCase(
            workload="overlay",
            dataset="fake",
            inputs={"left": ("left-shape",), "right": ("right-shape",)},
            note="fake overlay",
        )
    if workload == "lsi":
        return DatasetCase(
            workload="lsi",
            dataset="fake",
            inputs={"left": ("left",), "right": ("right",)},
            note="fake lsi",
        )
    return DatasetCase(
        workload="pip",
        dataset="fake",
        inputs={"points": ("point",), "polygons": ("shape",)},
        note="fake pip",
    )


class Goal2327RayJoinPreparedRouteContractTest(unittest.TestCase):
    def test_lsi_prepared_optix_route_reports_phase_boundaries(self) -> None:
        with (
            mock.patch.object(app, "_load_rayjoin_case", return_value=_case("lsi")),
            mock.patch("rtdsl.optix_runtime.pack_segments", return_value="packed-left"),
            mock.patch("rtdsl.optix_runtime.prepare_segment_pair_intersection_optix", return_value=_FakePrepared(9)),
        ):
            payload = app.run_rayjoin_prepared_optix_workload("lsi", result_mode="count")

        self.assertEqual(payload["execution_route"], "prepared_optix")
        self.assertEqual(payload["backend"], "optix")
        self.assertEqual(payload["row_count"], 9)
        self.assertEqual(payload["summary"]["output_contract"], "segment_segment_intersection_count")
        self.assertIn("query_pack_sec", payload["phases_sec"])
        self.assertIn("prepare_static_scene_sec", payload["phases_sec"])
        self.assertIn("prepared_query_sec", payload["phases_sec"])
        self.assertIn("native_query_sec", payload["native_phase_timings"])
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        self.assertIn("not_complete", payload["device_resident_continuation_status"])

    def test_pip_prepared_optix_route_can_keep_raw_rows_optional(self) -> None:
        with (
            mock.patch.object(app, "_load_rayjoin_case", return_value=_case("pip")),
            mock.patch("rtdsl.optix_runtime.pack_points", return_value="packed-points"),
            mock.patch("rtdsl.optix_runtime.pack_polygons", return_value="packed-shapes"),
            mock.patch("rtdsl.optix_runtime.prepare_point_closed_shape_membership_2d_optix", return_value=_FakePrepared(7)),
        ):
            payload = app.run_rayjoin_prepared_optix_workload(
                "pip",
                result_mode="rows",
                include_rows=False,
            )

        self.assertEqual(payload["row_count"], 7)
        self.assertEqual(payload["summary"]["output_contract"], "point_to_shape_positive_hit_rows")
        self.assertNotIn("rows", payload)
        self.assertIn("static_shape_pack_sec", payload["phases_sec"])

    def test_pip_device_filtered_count_mode_is_validated_and_explicit(self) -> None:
        with (
            mock.patch.object(app, "_load_rayjoin_case", return_value=_case("pip")),
            mock.patch("rtdsl.optix_runtime.pack_points", return_value="packed-points"),
            mock.patch("rtdsl.optix_runtime.pack_polygons", return_value="packed-shapes"),
            mock.patch("rtdsl.optix_runtime.prepare_point_closed_shape_membership_2d_optix", return_value=_FakePrepared(7)),
        ):
            payload = app.run_rayjoin_prepared_optix_workload(
                "pip",
                result_mode="count",
                count_mode="device_filtered_validated",
            )

        self.assertEqual(payload["count_mode"], "device_filtered_validated")
        self.assertEqual(payload["row_count"], 7)
        self.assertEqual(payload["summary"]["validation_exact_count"], 7)
        self.assertTrue(payload["summary"]["device_filtered_count_matches_exact"])
        self.assertFalse(payload["summary"]["device_filtered_is_exact_authority"])
        self.assertEqual(
            payload["summary"]["output_contract"],
            "point_to_shape_positive_hit_count_device_filtered_validated",
        )
        self.assertIn("validation_exact_query_sec", payload["phases_sec"])
        self.assertIn("prepared_query_sec", payload["phases_sec"])

    def test_pip_boundary_event_route_uses_generic_device_columns_without_membership_claim(self) -> None:
        pip_case = DatasetCase(
            workload="pip",
            dataset="fake",
            inputs={"points": ({"id": 0, "x": 0.0, "y": 0.0},), "polygons": ("shape",)},
            note="fake pip",
        )
        with (
            mock.patch.object(app, "_load_rayjoin_case", return_value=pip_case),
            mock.patch("rtdsl.optix_runtime.pack_points", return_value=_FakePackedPoints()),
            mock.patch("rtdsl.optix_runtime.pack_polygons", return_value="packed-shapes"),
            mock.patch("rtdsl.optix_runtime.prepare_point_closed_shape_membership_2d_optix", return_value=_FakePrepared(5)),
        ):
            payload = app.run_rayjoin_prepared_optix_workload(
                "pip",
                result_mode="count",
                count_mode="boundary_event_point_id_count_device_columns",
        )

        self.assertEqual(payload["count_mode"], "boundary_event_point_id_count_device_columns")
        self.assertEqual(payload["row_count"], 5)
        self.assertIsNone(payload["summary"]["positive_assignment_count"])
        self.assertEqual(payload["summary"]["boundary_event_row_count"], 5)
        self.assertTrue(payload["summary"]["boundary_event_contract_not_positive_membership"])
        self.assertEqual(
            payload["summary"]["output_contract"],
            "point_closed_shape_first_boundary_event_count_by_point_id_device_columns",
        )
        metadata = payload["summary"]["boundary_event_grouped_count_device_columns"]
        self.assertEqual(
            metadata["boundary_event_device_columns"]["runtime"]["output_residency"],
            "device_resident_boundary_event_columns",
        )
        self.assertEqual(
            metadata["point_id_grouped_count_device_columns"]["output_residency"],
            "device_resident_dense_grouped_count_column",
        )
        self.assertIn("not a PIP membership contract", payload["device_resident_continuation_status"])

    def test_device_filtered_count_mode_rejects_non_pip_or_rows(self) -> None:
        with self.assertRaisesRegex(ValueError, "only valid for PIP count"):
            app.run_rayjoin_prepared_optix_workload(
                "lsi",
                result_mode="count",
                count_mode="device_filtered_validated",
            )

        with self.assertRaisesRegex(ValueError, "only valid for PIP count"):
            app.run_rayjoin_prepared_optix_workload(
                "pip",
                result_mode="rows",
                count_mode="device_filtered_validated",
            )

    def test_overlay_prepared_optix_route_uses_generic_shape_pair_relation(self) -> None:
        with (
            mock.patch.object(app, "_load_rayjoin_case", return_value=_case("overlay_seed")),
            mock.patch("rtdsl.optix_runtime.pack_polygons", side_effect=("packed-left", "packed-right")),
            mock.patch("rtdsl.optix_runtime.prepare_shape_pair_relation_flags_optix", return_value=_FakePrepared(11)),
        ):
            payload = app.run_rayjoin_prepared_optix_workload(
                "overlay_seed",
                result_mode="count",
                include_rows=False,
            )

        self.assertEqual(payload["execution_route"], "prepared_optix")
        self.assertEqual(payload["row_count"], 11)
        self.assertEqual(payload["summary"]["output_contract"], "overlay_active_pair_dependency_count")
        self.assertEqual(payload["summary"]["active_seed_count"], 11)
        self.assertEqual(payload["native_phase_timings"]["native_count_mode"], "active_relation_flags")
        self.assertIn("query_pack_sec", payload["phases_sec"])
        self.assertIn("static_shape_pack_sec", payload["phases_sec"])
        self.assertIn("prepare_static_scene_sec", payload["phases_sec"])
        self.assertIn("prepared_query_sec", payload["phases_sec"])
        self.assertEqual(
            payload["device_resident_continuation_status"],
            "overlay_seed_prepared_pair_dependency_flags_complete",
        )
        self.assertIn("shape-pair", payload["native_engine_boundary"])

    def test_prepared_optix_suite_no_longer_marks_overlay_unsupported(self) -> None:
        def fake_run(workload: str, **_kwargs):
            return {
                "workload": workload,
                "phases_sec": {"prepared_query_sec": 0.25},
            }

        with mock.patch.object(app, "run_rayjoin_prepared_optix_workload", side_effect=fake_run):
            payload = app.run_rayjoin_suite(execution_route="prepared_optix", result_mode="count")

        self.assertEqual(set(payload["workloads"]), {"pip", "lsi", "overlay_seed"})
        self.assertNotIn("status", payload["workloads"]["overlay_seed"])
        self.assertEqual(payload["prepared_query_total_sec"], 0.75)


if __name__ == "__main__":
    unittest.main()
