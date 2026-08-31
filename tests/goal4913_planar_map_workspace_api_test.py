import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import rtdsl as rt
import rtdsl.optix_runtime as optix


ROOT = Path(__file__).resolve().parents[1]


def _packed(name="dataset"):
    return SimpleNamespace(
        name=name,
        point_count=3,
        edge_count=2,
        min_x=0.0,
        max_x=3.0,
        min_y=-1.0,
        max_y=2.0,
        lsi_segments=(f"{name}-lsi",),
        cdb_segments=(f"{name}-cdb",),
        points=(f"{name}-point",),
    )


class Goal4913PlanarMapWorkspaceApiTest(unittest.TestCase):
    def test_public_workspace_api_is_exported(self):
        self.assertIs(rt.PlanarMapWorkspace2DOptix, optix.PlanarMapWorkspace2DOptix)
        self.assertIs(rt.PlanarMapWorkspace2DOptixQuery, optix.PlanarMapWorkspace2DOptixQuery)
        self.assertIs(
            rt.prepare_planar_map_workspace_2d_optix,
            optix.prepare_planar_map_workspace_2d_optix,
        )
        self.assertIn("PlanarMapWorkspace2DOptix", rt.__all__)
        self.assertIn("PlanarMapWorkspace2DOptixQuery", rt.__all__)
        self.assertIn("prepare_planar_map_workspace_2d_optix", rt.__all__)

    def test_workspace_prepares_public_sessions_once_and_reuses_them(self):
        events = []

        class FakeLsiQuery:
            def run_pair_id_rows(self):
                events.append(("run_pair_id_rows",))
                return "pair-id-rows"

            def close(self):
                events.append(("close_lsi_query",))

        class FakeLsi:
            def prepare_query(self, query_segments):
                events.append(("prepare_lsi_query", query_segments))
                return FakeLsiQuery()

            def close(self):
                events.append(("close_lsi",))

        class FakeLocator:
            def __init__(self, label):
                self.label = label

            def run(self, points):
                events.append(("locator_run", self.label, points))
                return (self.label, points)

            def prepare_query_points(self, points):
                events.append(("prepare_query_points", self.label, points))
                return f"prepared-points-{self.label}-{points[0]}"

            def face_id_device_columns(self, prepared_points):
                events.append(("face_id_device_columns", self.label, prepared_points))
                return f"face-columns-{self.label}-{prepared_points}"

            def close(self):
                events.append(("close_locator", self.label))

        def fake_lsi(base_segments):
            events.append(("prepare_lsi_base", base_segments))
            return FakeLsi()

        def fake_locator(base_segments, *, query_map_id, scale_bounds):
            events.append(("prepare_locator", base_segments, query_map_id, scale_bounds))
            return FakeLocator(f"locator-{query_map_id}")

        left = _packed("left")
        right = _packed("right")
        with mock.patch.object(optix, "prepare_planar_map_lsi_2d_optix", fake_lsi), mock.patch.object(
            optix,
            "prepare_planar_map_point_location_2d_optix",
            fake_locator,
        ):
            with optix.prepare_planar_map_workspace_2d_optix(left, right) as workspace:
                self.assertEqual("pair-id-rows", workspace.run_lsi_pair_id_rows())
                self.assertEqual(("locator-0", left.points), workspace.run_left_points_in_right())
                self.assertEqual(("locator-1", right.points), workspace.run_right_points_in_left())
                self.assertEqual(
                    "prepared-points-locator-0-right-point",
                    workspace.prepare_base_points_for_queries(),
                )
                metadata = workspace.metadata()

        self.assertIn(("prepare_lsi_base", right.lsi_segments), events)
        self.assertIn(("prepare_lsi_query", left.lsi_segments), events)
        self.assertIn(("prepare_locator", right.cdb_segments, 0, (0.0, 3.0, -1.0, 2.0)), events)
        self.assertIn(("prepare_locator", left.cdb_segments, 1, (0.0, 3.0, -1.0, 2.0)), events)
        self.assertIn(("prepare_query_points", "locator-0", right.points), events)
        self.assertEqual("PLANAR_MAP_WORKSPACE_2D", metadata["workspace"])
        self.assertFalse(metadata["claim_boundary"]["bundled_rayjoin_helper_used"])
        self.assertFalse(metadata["claim_boundary"]["raw_optix_callback_exposed"])
        self.assertTrue(metadata["claim_boundary"]["public_generic_rtdl_workspace"])
        self.assertIn(("close_lsi_query",), events)
        self.assertIn(("close_lsi",), events)
        self.assertIn(("close_locator", "locator-0"), events)
        self.assertIn(("close_locator", "locator-1"), events)

    def test_workspace_query_prepares_distinct_query_lifecycle(self):
        events = []

        class FakeLsiQuery:
            def run_pair_id_rows(self):
                events.append(("run_query_pair_id_rows",))
                return "query-pair-id-rows"

            def close(self):
                events.append(("close_query_lsi",))

        class FakeLsi:
            def prepare_query(self, query_segments):
                events.append(("prepare_query_lsi", query_segments))
                return FakeLsiQuery()

            def close(self):
                events.append(("close_lsi",))

        class FakeLocator:
            def __init__(self, label):
                self.label = label

            def run(self, points):
                events.append(("locator_run", self.label, points))
                return (self.label, points)

            def prepare_query_points(self, points):
                events.append(("prepare_query_points", self.label, points))
                return f"prepared-points-{self.label}-{points[0]}"

            def face_id_device_columns(self, prepared_points):
                events.append(("face_id_device_columns", self.label, prepared_points))
                return f"face-columns-{self.label}-{prepared_points}"

            def close(self):
                events.append(("close_locator", self.label))

        def fake_lsi(base_segments):
            events.append(("prepare_base_lsi", base_segments))
            return FakeLsi()

        def fake_locator(base_segments, *, query_map_id, scale_bounds):
            events.append(("prepare_locator", base_segments, query_map_id, scale_bounds))
            return FakeLocator(f"locator-{query_map_id}-{base_segments[0]}")

        query_input = _packed("query")
        right = _packed("right")
        with mock.patch.object(optix, "prepare_planar_map_lsi_2d_optix", fake_lsi), mock.patch.object(
            optix,
            "prepare_planar_map_point_location_2d_optix",
            fake_locator,
        ):
            with optix.prepare_planar_map_workspace_2d_optix(
                _packed("left"),
                right,
                right_query_map_id=7,
            ) as workspace:
                shared_base_points = workspace.prepare_base_points_for_queries()
                with workspace.prepare_query(query_input) as query:
                    self.assertEqual("query-pair-id-rows", query.run_lsi_pair_id_rows())
                    self.assertEqual(("locator-0-right-cdb", query_input.points), query.run_query_points_in_base())
                    self.assertEqual(("locator-7-query-cdb", right.points), query.run_base_points_in_query())
                    query_points = query.prepare_query_points_in_base()
                    base_points = query.prepare_base_points_in_query()
                    self.assertEqual(
                        "face-columns-locator-0-right-cdb-prepared-points-locator-0-right-cdb-query-point",
                        query.query_points_in_base_face_id_device_columns(query_points),
                    )
                    self.assertEqual(
                        "face-columns-locator-7-query-cdb-prepared-points-locator-7-query-cdb-right-point",
                        query.base_points_in_query_face_id_device_columns(base_points),
                    )
                    self.assertEqual(
                        "face-columns-locator-7-query-cdb-prepared-points-locator-0-right-cdb-right-point",
                        query.base_points_in_query_face_id_device_columns(shared_base_points),
                    )
                    metadata = query.metadata()

        self.assertIn(("prepare_query_lsi", query_input.lsi_segments), events)
        self.assertIn(("prepare_locator", query_input.cdb_segments, 7, (0.0, 3.0, -1.0, 2.0)), events)
        self.assertIn(("prepare_query_points", "locator-0-right-cdb", right.points), events)
        self.assertIn(("prepare_query_points", "locator-0-right-cdb", query_input.points), events)
        self.assertIn(("prepare_query_points", "locator-7-query-cdb", right.points), events)
        self.assertIn(
            (
                "face_id_device_columns",
                "locator-0-right-cdb",
                "prepared-points-locator-0-right-cdb-query-point",
            ),
            events,
        )
        self.assertIn(
            (
                "face_id_device_columns",
                "locator-7-query-cdb",
                "prepared-points-locator-7-query-cdb-right-point",
            ),
            events,
        )
        self.assertEqual("PLANAR_MAP_WORKSPACE_2D_QUERY", metadata["workspace"])
        self.assertTrue(metadata["claim_boundary"]["public_generic_rtdl_workspace_query"])
        self.assertTrue(metadata["claim_boundary"]["query_specific_locator_prepare_still_paid"])
        self.assertFalse(metadata["claim_boundary"]["bundled_rayjoin_helper_used"])
        self.assertIn(("close_query_lsi",), events)
        self.assertIn(("close_locator", "locator-7-query-cdb"), events)

    def test_workspace_restores_packed_cache_env_when_loading_paths(self):
        events = []
        old_value = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
        os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = "original-cache"

        def fake_loader(path):
            events.append((str(path), os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")))
            return _packed(str(path))

        try:
            with mock.patch("rtdsl.datasets.load_planar_map_cdb_packed_inputs", fake_loader), mock.patch.object(
                optix,
                "prepare_planar_map_lsi_2d_optix",
                return_value=None,
            ), mock.patch.object(
                optix,
                "prepare_planar_map_point_location_2d_optix",
                return_value=None,
            ):
                workspace = optix.prepare_planar_map_workspace_2d_optix(
                    "left.cdb",
                    "right.cdb",
                    cache_dir="workspace-cache",
                    prepare_lsi=False,
                    prepare_point_location=False,
                )
                workspace.close()

            self.assertEqual(
                [("left.cdb", "workspace-cache"), ("right.cdb", "workspace-cache")],
                events,
            )
            self.assertEqual("original-cache", os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"))
        finally:
            if old_value is None:
                os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
            else:
                os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old_value

    def test_workspace_source_does_not_import_bundled_rayjoin_overlay(self):
        sys.modules.pop("rtdsl.rayjoin_overlay", None)
        source = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        workspace_source = source.split("class PlanarMapWorkspace2DOptix", 1)[1].split(
            "class PreparedOptixRayjoinCdbPointLocationPoints2D",
            1,
        )[0]
        self.assertNotIn("rayjoin_overlay", workspace_source)
        self.assertNotIn("RTDL_RAYJOIN_CDB_", workspace_source)


if __name__ == "__main__":
    unittest.main()
