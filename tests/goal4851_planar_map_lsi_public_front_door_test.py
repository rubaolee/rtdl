import os
import sys
import unittest
from pathlib import Path
from unittest import mock

import rtdsl as rt
import rtdsl.optix_runtime as optix


ROOT = Path(__file__).resolve().parents[1]


class Goal4851PlanarMapLsiPublicFrontDoorTest(unittest.TestCase):
    def test_public_api_is_exported(self):
        self.assertIs(rt.prepare_planar_map_lsi_2d_optix, optix.prepare_planar_map_lsi_2d_optix)
        self.assertIs(rt.PreparedOptixPlanarMapLsi2D, optix.PreparedOptixPlanarMapLsi2D)
        self.assertIs(rt.PreparedOptixPlanarMapLsi2DQuery, optix.PreparedOptixPlanarMapLsi2DQuery)
        self.assertIn("prepare_planar_map_lsi_2d_optix", rt.__all__)
        self.assertIn("PreparedOptixPlanarMapLsi2D", rt.__all__)
        self.assertIn("PreparedOptixPlanarMapLsi2DQuery", rt.__all__)
        self.assertEqual(
            "native",
            rt.engine_feature_support("planar_map_lsi_count_2d", "optix").status,
        )
        self.assertEqual(
            "unsupported_explicit",
            rt.engine_feature_support("planar_map_lsi_count_2d", "embree").status,
        )

    def test_front_door_passes_lsi_predicate_as_native_parameter_without_env_leak(self):
        events = []

        class FakePrepared:
            def count_prepared_left_exact_intersections(self, prepared_left, *, predicate_mode=None):
                events.append(
                    (
                        "count",
                        os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"),
                        predicate_mode,
                    )
                )
                return {
                    "count": 7,
                    "schema": "fake",
                    "native_symbol": optix.OPTIX_SEGMENT_PAIR_COUNT_PREPARED_LEFT_GROUPED_RANGE_DIRECT_INTERSECTION_WITH_PREDICATE_MODE_SYMBOL,
                    "predicate_mode": predicate_mode,
                    "predicate_selection": {
                        "mechanism": "native_abi_explicit_parameter",
                        "mode_id": predicate_mode,
                    },
                }

            def last_phase_timings(self):
                return {"mode": "fake_lsi"}

            def close(self):
                events.append(("close_prepared", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")))

        class FakePreparedLeft:
            def close(self):
                events.append(("close_left", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")))

        def fake_prepare_base(segments):
            events.append(("prepare_base", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"), len(segments)))
            return FakePrepared()

        def fake_prepare_left(segments):
            events.append(("prepare_left", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"), len(segments)))
            return FakePreparedLeft()

        os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", None)
        base = ({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},)
        query = ({"id": 2, "x0": 0.5, "y0": -1.0, "x1": 0.5, "y1": 1.0},)

        with mock.patch.object(optix, "prepare_segment_pair_intersection_optix", fake_prepare_base), mock.patch.object(
            optix,
            "prepare_segment_pair_left_set_optix",
            fake_prepare_left,
        ):
            with optix.prepare_planar_map_lsi_2d_optix(base) as prepared:
                result = prepared.count_with_metadata(query)

        self.assertIsNone(os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"))
        self.assertEqual(7, result["count"])
        self.assertEqual("PLANAR_MAP_LSI_2D", result["primitive"])
        self.assertFalse(result["claim_boundary"]["bundled_rayjoin_helper_used"])
        self.assertTrue(result["claim_boundary"]["public_generic_rtdl_primitive"])
        self.assertEqual("planar_map_lsi", result["native_predicate_mode"])
        self.assertEqual(1, result["native_predicate_mode_id"])
        self.assertEqual("rayjoin_lsi", result["native_predicate_legacy_alias"])
        self.assertEqual(
            "native_abi_explicit_parameter",
            result["predicate_selection"]["mechanism"],
        )
        self.assertEqual(1, result["predicate_selection"]["mode_id"])
        self.assertIn(("prepare_base", None, 1), events)
        self.assertIn(("prepare_left", None, 1), events)
        self.assertIn(("count", None, 1), events)

    def test_front_door_does_not_import_bundled_rayjoin_helper(self):
        sys.modules.pop("rtdsl.rayjoin_overlay", None)
        source = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        front_door = source.split("class PreparedOptixPlanarMapLsi2D", 1)[1].split(
            "def prepare_segment_pair_left_set_optix",
            1,
        )[0]
        self.assertNotIn("from .rayjoin_overlay", front_door)
        self.assertNotIn("import rtdsl.rayjoin_overlay", front_door)

    def test_pair_id_rows_front_door_uses_lightweight_native_route(self):
        events = []

        class FakePrepared:
            def run_prepared_left_grouped_range_direct_pair_id_rows(self, prepared_left, *, predicate_mode):
                events.append(
                    (
                        "pair_id_rows",
                        os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"),
                        predicate_mode,
                    )
                )
                return "pair-id-row-view"

            def close(self):
                events.append(("close_prepared", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")))

        class FakePreparedLeft:
            def close(self):
                events.append(("close_left", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")))

        def fake_prepare_base(segments):
            events.append(("prepare_base", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"), len(segments)))
            return FakePrepared()

        def fake_prepare_left(segments):
            events.append(("prepare_left", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"), len(segments)))
            return FakePreparedLeft()

        os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", None)
        base = ({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},)
        query = ({"id": 2, "x0": 0.5, "y0": -1.0, "x1": 0.5, "y1": 1.0},)

        with mock.patch.object(optix, "prepare_segment_pair_intersection_optix", fake_prepare_base), mock.patch.object(
            optix,
            "prepare_segment_pair_left_set_optix",
            fake_prepare_left,
        ):
            with optix.prepare_planar_map_lsi_2d_optix(base) as prepared:
                result = prepared.run_pair_id_rows(query)

        self.assertEqual("pair-id-row-view", result)
        self.assertIsNone(os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"))
        self.assertIn(("pair_id_rows", None, 1), events)

    def test_prepared_query_session_reuses_left_handle(self):
        events = []

        class FakePrepared:
            def count_prepared_left_exact_intersections(self, prepared_left, *, predicate_mode=None):
                events.append(("count", id(prepared_left), os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"), predicate_mode))
                return {
                    "count": 7,
                    "schema": "fake",
                    "native_symbol": optix.OPTIX_SEGMENT_PAIR_COUNT_PREPARED_LEFT_GROUPED_RANGE_DIRECT_INTERSECTION_WITH_PREDICATE_MODE_SYMBOL,
                    "predicate_mode": predicate_mode,
                }

            def run_prepared_left_grouped_range_direct_pair_id_rows(self, prepared_left, *, predicate_mode):
                events.append(("pair_id_rows", id(prepared_left), os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"), predicate_mode))
                return "pair-id-row-view"

            def last_phase_timings(self):
                return {"mode": "fake_lsi"}

            def close(self):
                events.append(("close_prepared", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")))

        class FakePreparedLeft:
            def close(self):
                events.append(("close_left", id(self), os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")))

        def fake_prepare_base(segments):
            events.append(("prepare_base", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"), len(segments)))
            return FakePrepared()

        def fake_prepare_left(segments):
            events.append(("prepare_left", os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"), len(segments)))
            return FakePreparedLeft()

        os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", None)
        base = ({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},)
        query = ({"id": 2, "x0": 0.5, "y0": -1.0, "x1": 0.5, "y1": 1.0},)

        with mock.patch.object(optix, "prepare_segment_pair_intersection_optix", fake_prepare_base), mock.patch.object(
            optix,
            "prepare_segment_pair_left_set_optix",
            fake_prepare_left,
        ):
            with optix.prepare_planar_map_lsi_2d_optix(base) as prepared:
                with prepared.prepare_query(query) as prepared_query:
                    metadata = prepared_query.count_with_metadata()
                    result = prepared_query.run_pair_id_rows()

        self.assertEqual(7, metadata["count"])
        self.assertTrue(metadata["query_prepare"]["prepared_query_reused"])
        self.assertEqual("pair-id-row-view", result)
        self.assertEqual(1, sum(1 for event in events if event[0] == "prepare_left"))
        count_handle_ids = [event[1] for event in events if event[0] == "count"]
        row_handle_ids = [event[1] for event in events if event[0] == "pair_id_rows"]
        self.assertEqual(count_handle_ids, row_handle_ids)
        self.assertIsNone(os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"))


if __name__ == "__main__":
    unittest.main()
