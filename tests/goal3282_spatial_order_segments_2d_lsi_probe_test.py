from __future__ import annotations

from dataclasses import dataclass
import unittest

import rtdsl as rt
from examples.current.research_benchmarks.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)


@dataclass(frozen=True)
class SegmentRow:
    id: int
    x0: float
    y0: float
    x1: float
    y1: float


class Goal3282SpatialOrderSegments2DLsiProbeTest(unittest.TestCase):
    def test_generic_segment_order_uses_centroid_and_preserves_ids(self) -> None:
        segments = (
            SegmentRow(30, 2.0, 0.0, 4.0, 0.0),
            SegmentRow(10, 1.0, 3.0, 3.0, 3.0),
            SegmentRow(20, 1.0, 2.0, 1.0, 2.0),
        )

        ordered = rt.spatial_order_segments_2d(segments, "x_then_y")

        self.assertEqual([segment.id for segment in ordered], [20, 10, 30])
        self.assertEqual(sorted(segment.id for segment in ordered), [10, 20, 30])

    def test_generic_segment_morton_order_is_deterministic(self) -> None:
        segments = (
            {"id": 4, "x0": 1.0, "y0": 1.0, "x1": 1.0, "y1": 1.0},
            {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 0.0, "y1": 0.0},
            {"id": 3, "x0": 1.0, "y0": 0.0, "x1": 1.0, "y1": 0.0},
            {"id": 2, "x0": 0.0, "y0": 1.0, "x1": 0.0, "y1": 1.0},
        )

        first = rt.spatial_order_segments_2d(segments, "morton_xy")
        second = rt.spatial_order_segments_2d(segments, "morton_xy")

        self.assertEqual([segment["id"] for segment in first], [1, 3, 2, 4])
        self.assertEqual([segment["id"] for segment in first], [segment["id"] for segment in second])

    def test_rayjoin_lsi_wrapper_delegates_to_generic_helper(self) -> None:
        segments = (
            {"id": 2, "x0": 0.0, "y0": 1.0, "x1": 0.0, "y1": 1.0},
            {"id": 1, "x0": 0.0, "y0": 0.0, "x1": 0.0, "y1": 0.0},
        )

        self.assertEqual(
            rayjoin_app._order_segments_for_locality(segments, "morton_xy"),
            rt.spatial_order_segments_2d(segments, "morton_xy"),
        )

    def test_discovery_exposes_segment_order_without_app_language(self) -> None:
        matches = rt.find_primitive(text="morton order segments before packing")

        self.assertTrue(matches)
        self.assertEqual(matches[0].node_id, "execution.spatial_order_segments_2d")
        description = rt.describe_primitive("execution.spatial_order_segments_2d")
        self.assertIn("intent:order", description["capability_tags"])
        self.assertNotIn("rayjoin", " ".join(description["aliases"]).lower())

    def test_invalid_segment_order_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "segment_order_mode"):
            rayjoin_app._order_segments_for_locality((), "bad_mode")

    def test_app_rejects_non_lsi_segment_order(self) -> None:
        with self.assertRaisesRegex(ValueError, "only valid for LSI"):
            rayjoin_app.run_rayjoin_prepared_optix_workload(
                "pip",
                dataset="tests/fixtures/rayjoin/br_county_subset.cdb",
                segment_order_mode="morton_xy",
            )


if __name__ == "__main__":
    unittest.main()
