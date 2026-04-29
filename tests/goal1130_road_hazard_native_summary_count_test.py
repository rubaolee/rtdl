import unittest
from unittest import mock

from examples import rtdl_road_hazard_screening as road


class Goal1130RoadHazardNativeSummaryCountTest(unittest.TestCase):
    def test_native_optix_summary_uses_prepared_threshold_count(self) -> None:
        class FakePrepared:
            def __init__(self) -> None:
                self.closed = False
                self.road_count = None
                self.threshold = None

            def count_at_least(self, roads, *, threshold):
                self.road_count = len(roads)
                self.threshold = threshold
                return 2

            def run(self, roads):
                raise AssertionError("native summary must not materialize hit-count rows")

            def close(self):
                self.closed = True

        fake = FakePrepared()
        with mock.patch.object(road.rt, "prepare_optix_segment_polygon_hitcount_2d", return_value=fake):
            with mock.patch.object(road.rt, "run_optix", side_effect=AssertionError("unexpected row path")):
                payload = road.run_case("optix", output_mode="summary", optix_mode="native")

        self.assertEqual(payload["priority_segment_count"], 2)
        self.assertEqual(payload["priority_segments"], [])
        self.assertEqual(payload["row_count"], 0)
        self.assertFalse(payload["summary_materializes_rows"])
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_native_hitcount_gated")
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(fake.road_count, 3)
        self.assertEqual(fake.threshold, 2)
        self.assertTrue(fake.closed)
        self.assertIn("native_prepare_sec", payload["run_phases"])
        self.assertIn("native_threshold_count_sec", payload["run_phases"])
        self.assertIn("native_close_sec", payload["run_phases"])

    def test_priority_segment_mode_still_materializes_ids(self) -> None:
        rows = (
            {"segment_id": 1, "hit_count": 2},
            {"segment_id": 2, "hit_count": 1},
            {"segment_id": 3, "hit_count": 2},
        )
        with mock.patch.object(road.rt, "run_optix", return_value=rows):
            payload = road.run_case("optix", output_mode="priority_segments", optix_mode="native")

        self.assertEqual(payload["priority_segments"], [1, 3])
        self.assertEqual(payload["priority_segment_count"], 2)
        self.assertEqual(payload["row_count"], 3)
        self.assertTrue(payload["summary_materializes_rows"])
        self.assertNotIn("rows", payload)
        self.assertIn("query_and_materialize_sec", payload["run_phases"])
        self.assertIn("summary_postprocess_sec", payload["run_phases"])


if __name__ == "__main__":
    unittest.main()
