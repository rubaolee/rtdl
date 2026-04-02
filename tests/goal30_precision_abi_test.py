from __future__ import annotations

import ctypes
import unittest

from rtdsl.embree_runtime import _RtdlPoint
from rtdsl.embree_runtime import _RtdlRay2D
from rtdsl.embree_runtime import _RtdlSegment
from rtdsl.embree_runtime import _RtdlTriangle
from rtdsl.embree_runtime import pack_polygons
from rtdsl.reference import Polygon


class Goal30PrecisionAbiTest(unittest.TestCase):
    def test_geometry_ctypes_use_double_precision_coordinates(self) -> None:
        segment_fields = dict(_RtdlSegment._fields_)
        point_fields = dict(_RtdlPoint._fields_)
        triangle_fields = dict(_RtdlTriangle._fields_)
        ray_fields = dict(_RtdlRay2D._fields_)

        for field_name in ("x0", "y0", "x1", "y1"):
            self.assertIs(segment_fields[field_name], ctypes.c_double)
        for field_name in ("x", "y"):
            self.assertIs(point_fields[field_name], ctypes.c_double)
        for field_name in ("x0", "y0", "x1", "y1", "x2", "y2"):
            self.assertIs(triangle_fields[field_name], ctypes.c_double)
        for field_name in ("ox", "oy", "dx", "dy", "tmax"):
            self.assertIs(ray_fields[field_name], ctypes.c_double)

    def test_packed_polygon_vertices_use_double_precision_array(self) -> None:
        packed = pack_polygons(
            records=(
                Polygon(id=1, vertices=((1.1, 2.2), (3.3, 4.4), (5.5, 6.6))),
            )
        )
        self.assertEqual(packed.vertex_xy_count, 6)
        self.assertEqual(type(packed.vertices_xy)._type_, ctypes.c_double)


if __name__ == "__main__":
    unittest.main()
