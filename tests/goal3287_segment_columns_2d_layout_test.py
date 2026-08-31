from __future__ import annotations

import ctypes
from dataclasses import dataclass
import inspect
import unittest

import rtdsl as rt
from examples.current.research_benchmarks.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)
from rtdsl import embree_runtime


@dataclass(frozen=True)
class SegmentRow:
    id: int
    x0: float
    y0: float
    x1: float
    y1: float


def _packed_ids(packed) -> list[int]:
    return [int(packed.records[index].id) for index in range(int(packed.count))]


class Goal3287SegmentColumns2DLayoutTest(unittest.TestCase):
    def test_segment_columns_preserve_ids_and_geometry(self) -> None:
        columns = rt.segment_columns_2d(
            (
                SegmentRow(10, 1.0, 2.0, 3.0, 4.0),
                SegmentRow(20, 5.0, 6.0, 7.0, 8.0),
            )
        )

        self.assertIsInstance(columns, rt.SegmentColumns2D)
        self.assertEqual(columns.count, 2)
        self.assertEqual([int(value) for value in columns.ids], [10, 20])
        self.assertEqual([float(value) for value in columns.x1], [3.0, 7.0])

    def test_segment_columns_can_order_and_pack(self) -> None:
        columns = rt.segment_columns_2d(
            (
                {"id": 30, "x0": 2.0, "y0": 0.0, "x1": 4.0, "y1": 0.0},
                {"id": 10, "x0": 1.0, "y0": 3.0, "x1": 3.0, "y1": 3.0},
                {"id": 20, "x0": 1.0, "y0": 2.0, "x1": 1.0, "y1": 2.0},
            ),
            order_mode="y_then_x",
        )

        packed = embree_runtime.pack_segments(records=columns)

        self.assertEqual([int(value) for value in columns.ids], [30, 20, 10])
        self.assertEqual(_packed_ids(packed), [30, 20, 10])

    def test_segment_columns_pack_to_numpy_owned_native_abi_buffer(self) -> None:
        columns = rt.segment_columns_2d(
            ids=[7, 8],
            x0=[0.25, 1.25],
            y0=[0.5, 1.5],
            x1=[2.25, 3.25],
            y1=[2.5, 3.5],
        )

        packed = embree_runtime.pack_segments(records=columns)

        self.assertIsNotNone(packed.owner)
        self.assertEqual(packed.owner.dtype.itemsize, ctypes.sizeof(embree_runtime._RtdlSegment))
        self.assertEqual(packed.owner.dtype.fields["id"][1], embree_runtime._RtdlSegment.id.offset)
        self.assertEqual(packed.owner.dtype.fields["x0"][1], embree_runtime._RtdlSegment.x0.offset)
        self.assertEqual(_packed_ids(packed), [7, 8])
        self.assertAlmostEqual(float(packed.records[1].x1), 3.25)

    def test_natural_segment_records_pack_to_numpy_owned_native_abi_buffer(self) -> None:
        packed = embree_runtime.pack_segments(
            records=(
                SegmentRow(11, 0.0, 1.0, 2.0, 3.0),
                SegmentRow(12, 4.0, 5.0, 6.0, 7.0),
            )
        )

        self.assertIsNotNone(packed.owner)
        self.assertEqual(_packed_ids(packed), [11, 12])
        self.assertAlmostEqual(float(packed.records[0].y1), 3.0)

    def test_segment_columns_with_ids_remaps_without_changing_geometry_columns(self) -> None:
        columns = rt.segment_columns_2d(
            ids=[101, 202],
            x0=[0.0, 1.0],
            y0=[0.0, 1.0],
            x1=[2.0, 3.0],
            y1=[2.0, 3.0],
        )
        remapped = rt.segment_columns_with_ids(columns, range(columns.count))
        packed = embree_runtime.pack_segments(records=remapped)

        self.assertEqual([int(value) for value in remapped.ids], [0, 1])
        self.assertIs(remapped.x0, columns.x0)
        self.assertEqual(_packed_ids(packed), [0, 1])

    def test_segment_columns_keep_wide_ids_until_pack_time_then_fail_closed(self) -> None:
        columns = rt.segment_columns_2d(
            ids=[1 << 32],
            x0=[0.0],
            y0=[0.0],
            x1=[1.0],
            y1=[1.0],
        )

        self.assertEqual(int(columns.ids[0]), 1 << 32)
        with self.assertRaisesRegex(ValueError, "uint32 packed segment ABI"):
            embree_runtime.pack_segments(records=columns)

    def test_discovery_exposes_segment_columns_without_app_language(self) -> None:
        matches = rt.find_primitive(text="cache segment column arrays while preserving caller ids")

        self.assertTrue(matches)
        self.assertEqual(matches[0].node_id, "execution.segment_columns_2d")
        description = rt.describe_primitive("execution.segment_columns_2d")
        self.assertIn("intent:prepare", description["capability_tags"])
        self.assertNotIn("rayjoin", " ".join(description["aliases"]).lower())

    def test_rayjoin_compact_left_pack_uses_generic_segment_columns(self) -> None:
        source = inspect.getsource(rayjoin_app.RayJoinOptixCompactGroupedCountPackedLeftSegments)

        self.assertIn("segment_columns_2d", source)
        self.assertIn("segment_columns_with_ids", source)
        self.assertNotIn("tuple(_segment_record_dict(segment) for segment in left_segments)", source)


if __name__ == "__main__":
    unittest.main()
