import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_road_hazard_screening as road
from examples import rtdl_segment_polygon_anyhit_rows as anyhit
from examples import rtdl_segment_polygon_hitcount as hitcount


class Goal956SegmentPolygonNativeContinuationMetadataTest(unittest.TestCase):
    def test_segment_polygon_hitcount_native_mode_reports_gated_native_continuation(self) -> None:
        with mock.patch.object(hitcount.rt, "run_optix", return_value=({"segment_id": 1, "hit_count": 1},)):
            payload = hitcount.run_case(
                "optix",
                "authored_segment_polygon_minimal",
                optix_mode="native",
            )

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_native_hitcount_gated")
        self.assertFalse(payload["rt_core_accelerated"])

    def test_road_hazard_native_mode_reports_gated_native_continuation(self) -> None:
        with mock.patch.object(road.rt, "run_optix", return_value=({"segment_id": 1, "hit_count": 2},)):
            payload = road.run_case("optix", optix_mode="native")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_native_hitcount_gated")
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(payload["priority_segments"], [1])

    def test_road_hazard_native_summary_uses_threshold_count_without_rows(self) -> None:
        class FakePrepared:
            def __init__(self) -> None:
                self.closed = False

            def count_at_least(self, roads, *, threshold):
                self.road_count = len(roads)
                self.threshold = threshold
                return 2

            def run(self, roads):
                raise AssertionError("summary mode should not materialize hit-count rows")

            def close(self):
                self.closed = True

        fake = FakePrepared()
        with mock.patch.object(road.rt, "prepare_optix_segment_polygon_hitcount_2d", return_value=fake):
            payload = road.run_case("optix", output_mode="summary", optix_mode="native")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_native_hitcount_gated")
        self.assertFalse(payload["summary_materializes_rows"])
        self.assertEqual(payload["priority_segment_count"], 2)
        self.assertEqual(payload["priority_segments"], [])
        self.assertEqual(fake.threshold, 2)
        self.assertEqual(fake.road_count, 3)
        self.assertTrue(fake.closed)
        self.assertIn("native_threshold_count_sec", payload["run_phases"])

    def test_anyhit_native_pair_rows_reports_rt_core_pair_row_path(self) -> None:
        with mock.patch.object(
            anyhit.rt,
            "segment_polygon_anyhit_rows_native_bounded_optix",
            return_value=({"segment_id": 1, "polygon_id": 10},),
        ):
            payload = anyhit.run_case(
                "optix",
                "authored_segment_polygon_minimal",
                output_mode="rows",
                optix_mode="native",
                require_rt_core=True,
            )

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_native_bounded_pair_rows")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertEqual(payload["row_count"], 1)

    def test_anyhit_compact_native_hitcount_is_gated_not_claimed(self) -> None:
        with mock.patch.object(
            anyhit.rt,
            "run_optix",
            return_value=({"segment_id": 1, "hit_count": 2},),
        ):
            payload = anyhit.run_case(
                "optix",
                "authored_segment_polygon_minimal",
                output_mode="segment_counts",
                optix_mode="native",
            )

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_native_hitcount_gated")
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(payload["segment_counts"], ({"segment_id": 1, "hit_count": 2},))

    def test_cpu_segment_polygon_paths_do_not_report_native_continuation(self) -> None:
        payload = anyhit.run_case(
            "cpu_python_reference",
            "authored_segment_polygon_minimal",
            output_mode="segment_flags",
        )

        self.assertFalse(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "none")
        self.assertFalse(payload["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
