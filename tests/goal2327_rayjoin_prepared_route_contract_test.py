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


class _FakePrepared:
    def __init__(self, row_count: int):
        self.row_count = row_count
        self.closed = False

    def count(self, _packed):
        return self.row_count

    def run_raw(self, _packed, **_kwargs):
        return _FakeRawView(self.row_count)

    def last_phase_timings(self):
        return {
            "native_query_sec": 0.001,
            "candidate_count": self.row_count,
        }

    def close(self) -> None:
        self.closed = True


def _case(workload: str) -> DatasetCase:
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

    def test_prepared_optix_route_rejects_overlay_until_continuation_exists(self) -> None:
        with self.assertRaisesRegex(ValueError, "supports only"):
            app.run_rayjoin_prepared_optix_workload("overlay_seed")


if __name__ == "__main__":
    unittest.main()
