import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import rtdsl as rt
import rtdsl.optix_runtime as optix


ROOT = Path(__file__).resolve().parents[1]


class Goal4857PlanarMapPointLocationPublicFrontDoorTest(unittest.TestCase):
    def test_public_api_is_exported(self):
        self.assertIs(
            rt.prepare_planar_map_point_location_2d_optix,
            optix.prepare_planar_map_point_location_2d_optix,
        )
        self.assertIs(
            rt.PreparedOptixPlanarMapPointLocation2D,
            optix.PreparedOptixPlanarMapPointLocation2D,
        )
        self.assertIn("prepare_planar_map_point_location_2d_optix", rt.__all__)
        self.assertIn("PreparedOptixPlanarMapPointLocation2D", rt.__all__)
        self.assertEqual(
            "native",
            rt.engine_feature_support("planar_map_point_location_2d", "optix").status,
        )

    def test_dataset_public_aliases_are_exported(self):
        from rtdsl import CdbChain, CdbDataset, CdbPoint

        dataset = CdbDataset(
            name="tiny",
            chains=(
                CdbChain(
                    chain_id=7,
                    point_count=2,
                    first_point_id=1,
                    last_point_id=2,
                    left_face_id=11,
                    right_face_id=13,
                    points=(CdbPoint(0.0, 0.0), CdbPoint(1.0, 0.0)),
                ),
            ),
        )
        segments = rt.chains_to_planar_map_segments(dataset)
        points = rt.chains_to_planar_map_points(dataset)
        self.assertEqual(1, len(segments))
        self.assertEqual(11, segments[0]["left_face_id"])
        self.assertEqual(13, segments[0]["right_face_id"])
        self.assertEqual(2, len(points))
        self.assertIn("chains_to_planar_map_segments", rt.__all__)
        self.assertIn("chains_to_planar_map_points", rt.__all__)

    def test_front_door_hides_legacy_env_bridge_and_restores_environment(self):
        events = []

        class FakeRows:
            row_count = 2
            rows_ptr = (
                SimpleNamespace(segment_id=3, face_id=10),
                SimpleNamespace(segment_id=0xFFFFFFFF, face_id=0),
            )

            def close(self):
                events.append(("rows_closed", os.environ.get("RTDL_RAYJOIN_CDB_QUERY_MAP_ID")))

        class FakePrepared:
            def run_raw(self, points):
                events.append(
                    (
                        "run_raw",
                        os.environ.get("RTDL_RAYJOIN_CDB_QUERY_MAP_ID"),
                        os.environ.get("RTDL_RAYJOIN_CDB_SCALE_MIN_X"),
                        os.environ.get("RTDL_RAYJOIN_CDB_SCALE_MAX_Y"),
                    )
                )
                return FakeRows()

            def count_positive_faces(self, points):
                events.append(("count_positive_faces", os.environ.get("RTDL_RAYJOIN_CDB_QUERY_MAP_ID")))
                return 5

            def last_phase_timings(self):
                return {"traversal": 0.25}

            def close(self):
                events.append(("close", os.environ.get("RTDL_RAYJOIN_CDB_QUERY_MAP_ID")))

        def fake_prepare(segments):
            events.append(("prepare", len(segments), os.environ.get("RTDL_RAYJOIN_CDB_QUERY_MAP_ID")))
            return FakePrepared()

        base = ({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},)
        old = {
            key: os.environ.get(key)
            for key in (
                "RTDL_RAYJOIN_CDB_QUERY_MAP_ID",
                "RTDL_RAYJOIN_CDB_SCALE_MIN_X",
                "RTDL_RAYJOIN_CDB_SCALE_MAX_Y",
            )
        }
        for key in old:
            os.environ.pop(key, None)
        try:
            with mock.patch.object(optix, "prepare_rayjoin_cdb_point_location_2d_optix", fake_prepare):
                with optix.prepare_planar_map_point_location_2d_optix(
                    base,
                    query_map_id=1,
                    scale_bounds=(-2.0, 3.0, -4.0, 5.0),
                ) as locator:
                    self.assertEqual(5, locator.count_positive_faces(("points",)))
                    metadata = locator.count_with_metadata(("points",))
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertIsNone(os.environ.get("RTDL_RAYJOIN_CDB_QUERY_MAP_ID"))
        self.assertIn(("prepare", 1, "1"), events)
        self.assertIn(("count_positive_faces", "1"), events)
        self.assertIn(("run_raw", "1", "-2.0", "5.0"), events)
        self.assertEqual("PLANAR_MAP_POINT_LOCATION_2D", metadata["primitive"])
        self.assertEqual(1, metadata["located_segment_count"])
        self.assertEqual(1, metadata["positive_face_count"])
        self.assertFalse(metadata["claim_boundary"]["bundled_rayjoin_helper_used"])
        self.assertTrue(metadata["claim_boundary"]["public_generic_rtdl_primitive"])

    def test_front_door_accepts_packed_directed_segments_without_tuple_materialization(self):
        from rtdsl.embree_runtime import PackedRayjoinCdbSegments

        events = []
        packed = PackedRayjoinCdbSegments(records=object(), count=123, owner="owner")

        class FakePrepared:
            def close(self):
                events.append("close")

        def fake_prepare(segments):
            events.append(("prepare_is_same_object", segments is packed, getattr(segments, "count", None)))
            return FakePrepared()

        with mock.patch.object(optix, "prepare_rayjoin_cdb_point_location_2d_optix", fake_prepare):
            with optix.prepare_planar_map_point_location_2d_optix(packed) as locator:
                self.assertEqual(123, locator.base_segment_count)

        self.assertIn(("prepare_is_same_object", True, 123), events)
        self.assertIn("close", events)

    def test_front_door_sets_scale_environment_during_prepare(self):
        events = []

        class FakePrepared:
            def close(self):
                pass

        def fake_prepare(segments):
            events.append(
                (
                    os.environ.get("RTDL_RAYJOIN_CDB_QUERY_MAP_ID"),
                    os.environ.get("RTDL_RAYJOIN_CDB_SCALE_MIN_X"),
                    os.environ.get("RTDL_RAYJOIN_CDB_SCALE_MAX_X"),
                    os.environ.get("RTDL_RAYJOIN_CDB_SCALE_MIN_Y"),
                    os.environ.get("RTDL_RAYJOIN_CDB_SCALE_MAX_Y"),
                )
            )
            return FakePrepared()

        with mock.patch.object(optix, "prepare_rayjoin_cdb_point_location_2d_optix", fake_prepare):
            with optix.prepare_planar_map_point_location_2d_optix(
                ({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},),
                query_map_id=0,
                scale_bounds=(10.0, 20.0, 30.0, 40.0),
            ):
                pass

        self.assertEqual([("0", "10.0", "20.0", "30.0", "40.0")], events)

    def test_section53_internal_runner_uses_public_planar_map_front_door(self):
        runner = (
            ROOT / "history" / "internal_docs" / "goal4855_rayjoin_section53_pip_public_front_door.py"
        ).read_text(encoding="utf-8")
        raw_diag = (
            ROOT / "history" / "internal_docs" / "goal4856_rtdl_section53_pip_raw_diagnostic.py"
        ).read_text(encoding="utf-8")
        self.assertIn("prepare_planar_map_point_location_2d_optix", runner)
        self.assertIn("prepare_planar_map_point_location_2d_optix", raw_diag)
        self.assertNotIn("def _point_location_env", runner)
        self.assertNotIn("from goal4855_rayjoin_section53_pip_public_front_door import _point_location_env", raw_diag)
        self.assertNotIn("prepare_directed_segment_point_location_2d_optix", runner)
        self.assertNotIn("prepare_directed_segment_point_location_2d_optix", raw_diag)
        sys.modules.pop("rtdsl.rayjoin_overlay", None)


if __name__ == "__main__":
    unittest.main()
