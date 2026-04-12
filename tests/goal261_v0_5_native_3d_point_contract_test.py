import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.embree_runtime import _pack_for_geometry as embree_pack_for_geometry
from rtdsl.embree_runtime import pack_points as embree_pack_points
from rtdsl.optix_runtime import _pack_for_geometry as optix_pack_for_geometry
from rtdsl.optix_runtime import pack_points as optix_pack_points
from rtdsl.vulkan_runtime import _pack_for_geometry as vulkan_pack_for_geometry
from rtdsl.vulkan_runtime import PackedPoints as VulkanPackedPoints


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_3d_native_boundary_kernel():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


class Goal261V05Native3DPointContractTest(unittest.TestCase):
    def test_embree_pack_points_supports_point3d_records(self) -> None:
        packed = embree_pack_points(records=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),))
        self.assertEqual(packed.count, 1)
        self.assertEqual(packed.dimension, 3)

    def test_optix_pack_points_supports_point3d_records(self) -> None:
        packed = optix_pack_points(records=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),))
        self.assertEqual(packed.count, 1)
        self.assertEqual(packed.dimension, 3)

    def test_vulkan_prepared_path_supports_points3d(self) -> None:
        compiled = rt.compile_kernel(fixed_radius_neighbors_3d_native_boundary_kernel)
        packed = vulkan_pack_for_geometry(compiled.inputs[0], (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),))
        self.assertIsInstance(packed, VulkanPackedPoints)
        self.assertEqual(packed.count, 1)
        self.assertEqual(packed.dimension, 3)

    def test_embree_prepared_path_supports_points3d_for_fixed_radius(self) -> None:
        compiled = rt.compile_kernel(fixed_radius_neighbors_3d_native_boundary_kernel)
        packed = embree_pack_for_geometry(compiled.inputs[0], (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),))
        self.assertEqual(packed.count, 1)
        self.assertEqual(packed.dimension, 3)

    def test_optix_prepared_path_supports_points3d(self) -> None:
        compiled = rt.compile_kernel(fixed_radius_neighbors_3d_native_boundary_kernel)
        packed = optix_pack_for_geometry(compiled.inputs[0], (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),))
        self.assertEqual(packed.count, 1)
        self.assertEqual(packed.dimension, 3)


if __name__ == "__main__":
    unittest.main()
