from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
INTERNAL = ROOT / "history" / "internal_docs"
for path in (SRC, INTERNAL):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

import goal4954c_grouped_carrier_measure as grouped  # noqa: E402
import goal4955_projected_descriptor_pipeline_measure as projected  # noqa: E402


base = grouped.base


def _dataset(*, left_face: int, right_face: int, points: list[tuple[float, float]]):
    point_x = np.asarray([point[0] for point in points], dtype=np.float64)
    point_y = np.asarray([point[1] for point in points], dtype=np.float64)
    return SimpleNamespace(
        chain_count=1,
        chain_offsets=np.asarray([0], dtype=np.int64),
        chain_point_counts=np.asarray([len(points)], dtype=np.int64),
        chain_left_faces=np.asarray([left_face], dtype=np.int64),
        chain_right_faces=np.asarray([right_face], dtype=np.int64),
        point_x=point_x,
        point_y=point_y,
    )


def _xsect(*, side: int, edge: int, other_edge: int, x: float, y: float, midpoint_face: int):
    row = base.OverlayIntersection(
        eid0=edge if side == 0 else other_edge,
        eid1=other_edge if side == 0 else edge,
        x=x,
        y=y,
        display_x=x,
        display_y=y,
        scaled_x=int(round(x * 100)),
        scaled_y=int(round(y * 100)),
    )
    if side == 0:
        row.mid_point_polygon_id_map0 = midpoint_face
    else:
        row.mid_point_polygon_id_map1 = midpoint_face
    return row


class Goal4955ProjectedDescriptorPipelineTest(unittest.TestCase):
    def test_projected_descriptor_carrier_matches_full_grouped_descriptor_result(self) -> None:
        left = _dataset(left_face=10, right_face=20, points=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)])
        right = _dataset(left_face=30, right_face=40, points=[(0.0, 1.0), (1.0, 1.0)])
        xsects0 = [
            _xsect(side=0, edge=0, other_edge=0, x=0.25, y=0.0, midpoint_face=150),
            _xsect(side=0, edge=0, other_edge=1, x=0.75, y=0.0, midpoint_face=150),
        ]
        xsects1 = [
            _xsect(side=1, edge=0, other_edge=0, x=0.25, y=1.0, midpoint_face=250),
            _xsect(side=1, edge=0, other_edge=1, x=0.75, y=1.0, midpoint_face=250),
        ]
        point_faces = (
            np.asarray([100, 100, 100], dtype=np.uint32),
            np.asarray([200, 200], dtype=np.uint32),
        )

        full_carrier, full_stats = grouped.build_grouped_columnar_carrier(
            (left, right),
            (xsects0, xsects1),
            point_faces,
        )
        projected_carrier, projected_stats = projected.build_projected_descriptor_carrier(
            (left, right),
            (xsects0, xsects1),
            point_faces,
        )

        self.assertIn("x", full_carrier)
        self.assertIn("y", full_carrier)
        self.assertNotIn("x", projected_carrier)
        self.assertNotIn("y", projected_carrier)
        self.assertNotIn("alt_label", projected_carrier)
        self.assertNotIn("source_side_id", projected_carrier)
        self.assertNotIn("source_element_id", projected_carrier)
        self.assertFalse(projected_stats["geometry_payload_columns_materialized"])
        self.assertTrue(projected_stats["projection_pushdown"])

        self.assertEqual(full_stats["group_count"], projected_stats["group_count"])
        self.assertEqual(full_stats["point_row_count"], projected_stats["point_row_count"])
        self.assertEqual(full_stats["skipped_group_count"], projected_stats["skipped_group_count"])
        for field in ("group_offset", "group_length", "label_a", "label_b"):
            np.testing.assert_array_equal(full_carrier[field], projected_carrier[field])

        full_result = grouped.descriptor_pair_count_grouped(full_carrier)
        projected_result = projected.descriptor_pair_count_projected(projected_carrier)
        self.assertEqual(full_result["pair_count"], projected_result["pair_count"])
        self.assertEqual(full_result["total_groups"], projected_result["total_groups"])
        self.assertEqual(full_result["total_point_rows"], projected_result["total_point_rows"])
        self.assertEqual(full_result["top_pairs_by_point_rows"], projected_result["top_pairs_by_point_rows"])


if __name__ == "__main__":
    unittest.main()
