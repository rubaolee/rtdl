"""Regression tests: Packed* classes from embree_runtime are the canonical
shared types; optix_runtime must accept them without re-packing.

These tests exercise the structural interop contract without requiring the
actual OptiX or Embree native libraries to be installed.
"""

import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl import embree_runtime, optix_runtime


class PackedClassIdentityTest(unittest.TestCase):
    """Packed* classes exported at the top-level must be the same objects
    as those in embree_runtime — not independent re-definitions."""

    def test_packed_segments_is_canonical(self):
        self.assertIs(rt.PackedSegments, embree_runtime.PackedSegments)

    def test_packed_points_is_canonical(self):
        self.assertIs(rt.PackedPoints, embree_runtime.PackedPoints)

    def test_packed_polygons_is_canonical(self):
        self.assertIs(rt.PackedPolygons, embree_runtime.PackedPolygons)

    def test_packed_triangles_is_canonical(self):
        self.assertIs(rt.PackedTriangles, embree_runtime.PackedTriangles)

    def test_packed_rays_is_canonical(self):
        self.assertIs(rt.PackedRays, embree_runtime.PackedRays)


class OptixImportsCanonicalPackedTest(unittest.TestCase):
    """optix_runtime must re-use the exact same Packed* classes as embree_runtime."""

    def test_optix_packed_segments_is_embree_packed_segments(self):
        self.assertIs(optix_runtime.PackedSegments, embree_runtime.PackedSegments)

    def test_optix_packed_points_is_embree_packed_points(self):
        self.assertIs(optix_runtime.PackedPoints, embree_runtime.PackedPoints)

    def test_optix_packed_polygons_is_embree_packed_polygons(self):
        self.assertIs(optix_runtime.PackedPolygons, embree_runtime.PackedPolygons)

    def test_optix_packed_triangles_is_embree_packed_triangles(self):
        self.assertIs(optix_runtime.PackedTriangles, embree_runtime.PackedTriangles)

    def test_optix_packed_rays_is_embree_packed_rays(self):
        self.assertIs(optix_runtime.PackedRays, embree_runtime.PackedRays)


class EmbreePackedIsInstanceOfCanonicalTest(unittest.TestCase):
    """Objects built by embree pack_* helpers must be instances of the canonical
    Packed* classes so that optix_runtime._pack_for_geometry passes them through."""

    def test_pack_segments_yields_canonical_type(self):
        packed = rt.pack_segments(ids=[1], x0=[0.0], y0=[0.0], x1=[1.0], y1=[1.0])
        self.assertIsInstance(packed, rt.PackedSegments)
        self.assertIsInstance(packed, optix_runtime.PackedSegments)

    def test_pack_points_yields_canonical_type(self):
        packed = rt.pack_points(ids=[1], x=[0.5], y=[0.5])
        self.assertIsInstance(packed, rt.PackedPoints)
        self.assertIsInstance(packed, optix_runtime.PackedPoints)

    def test_pack_triangles_yields_canonical_type(self):
        packed = rt.pack_triangles(
            ids=[1],
            x0=[0.0], y0=[0.0],
            x1=[1.0], y1=[0.0],
            x2=[0.0], y2=[1.0],
        )
        self.assertIsInstance(packed, rt.PackedTriangles)
        self.assertIsInstance(packed, optix_runtime.PackedTriangles)

    def test_pack_rays_yields_canonical_type(self):
        packed = rt.pack_rays(
            ids=[1], ox=[0.0], oy=[0.0], dx=[1.0], dy=[0.0], tmax=[1e9]
        )
        self.assertIsInstance(packed, rt.PackedRays)
        self.assertIsInstance(packed, optix_runtime.PackedRays)

    def test_pack_polygons_yields_canonical_type(self):
        packed = rt.pack_polygons(
            ids=[1],
            vertex_offsets=[0],
            vertex_counts=[4],
            vertices_xy=[0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0],
        )
        self.assertIsInstance(packed, rt.PackedPolygons)
        self.assertIsInstance(packed, optix_runtime.PackedPolygons)


class OptixPackForGeometryPassThroughTest(unittest.TestCase):
    """optix_runtime._pack_for_geometry must accept embree-packed objects
    without re-packing (returns the same object unchanged)."""

    def test_packed_segments_passed_through(self):
        packed = rt.pack_segments(ids=[1], x0=[0.0], y0=[0.0], x1=[1.0], y1=[1.0])
        result = optix_runtime._pack_for_geometry("segments", packed)
        self.assertIs(result, packed)

    def test_packed_points_passed_through(self):
        packed = rt.pack_points(ids=[1], x=[0.5], y=[0.5])
        result = optix_runtime._pack_for_geometry("points", packed)
        self.assertIs(result, packed)

    def test_packed_triangles_passed_through(self):
        packed = rt.pack_triangles(
            ids=[1],
            x0=[0.0], y0=[0.0],
            x1=[1.0], y1=[0.0],
            x2=[0.0], y2=[1.0],
        )
        result = optix_runtime._pack_for_geometry("triangles", packed)
        self.assertIs(result, packed)

    def test_packed_rays_passed_through(self):
        packed = rt.pack_rays(
            ids=[1], ox=[0.0], oy=[0.0], dx=[1.0], dy=[0.0], tmax=[1e9]
        )
        result = optix_runtime._pack_for_geometry("rays", packed)
        self.assertIs(result, packed)

    def test_packed_polygons_passed_through(self):
        packed = rt.pack_polygons(
            ids=[1],
            vertex_offsets=[0],
            vertex_counts=[4],
            vertices_xy=[0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0],
        )
        result = optix_runtime._pack_for_geometry("polygons", packed)
        self.assertIs(result, packed)


class OptixCtypeStructSharedTest(unittest.TestCase):
    """Input ctypes structs used by optix must be the same objects as those
    in embree_runtime so that ctypes argtypes checking passes for either backend's
    packed arrays."""

    def test_rtdl_segment_struct_is_shared(self):
        self.assertIs(optix_runtime._RtdlSegment, embree_runtime._RtdlSegment)

    def test_rtdl_point_struct_is_shared(self):
        self.assertIs(optix_runtime._RtdlPoint, embree_runtime._RtdlPoint)

    def test_rtdl_polygon_ref_struct_is_shared(self):
        self.assertIs(optix_runtime._RtdlPolygonRef, embree_runtime._RtdlPolygonRef)

    def test_rtdl_triangle_struct_is_shared(self):
        self.assertIs(optix_runtime._RtdlTriangle, embree_runtime._RtdlTriangle)

    def test_rtdl_ray2d_struct_is_shared(self):
        self.assertIs(optix_runtime._RtdlRay2D, embree_runtime._RtdlRay2D)


if __name__ == "__main__":
    unittest.main()
