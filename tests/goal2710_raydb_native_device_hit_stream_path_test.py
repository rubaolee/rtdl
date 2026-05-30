import unittest
from pathlib import Path

import rtdsl as rt
from rtdsl.reference import Ray3D
from rtdsl.reference import Triangle3D


ROOT = Path(__file__).resolve().parents[1]


class Goal2710RaydbNativeDeviceHitStreamPathTest(unittest.TestCase):
    def test_experimental_generic_device_column_front_door_is_not_public_all(self) -> None:
        self.assertTrue(hasattr(rt, "run_generic_ray_triangle_hit_stream_device_columns_3d"))
        self.assertNotIn("run_generic_ray_triangle_hit_stream_device_columns_3d", rt.__all__)

    def test_device_column_front_door_fails_closed_for_non_optix_backend(self) -> None:
        rays = (Ray3D(0, 0.0, 0.0, -1.0, 0.0, 0.0, 1.0, 2.0),)
        triangles = (Triangle3D(0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),)

        with self.assertRaisesRegex(ValueError, "require backend='optix'"):
            rt.run_generic_ray_triangle_hit_stream_device_columns_3d(
                rays,
                triangles,
                backend="cpu",
            )

    def test_generic_front_door_delegates_only_to_optix_device_columns(self) -> None:
        source = (ROOT / "src" / "rtdsl" / "generic_primitives.py").read_text()

        self.assertIn("def run_generic_ray_triangle_hit_stream_device_columns_3d", source)
        self.assertIn("ray_triangle_hit_stream_device_columns_3d_optix", source)
        self.assertIn("currently has only an OptiX implementation", source)
        self.assertIn("device-column ray/triangle hit streams currently require backend='optix'", source)

    def test_raydb_optix_device_mode_uses_native_columns_before_triton_gather(self) -> None:
        source = (
            ROOT
            / "examples"
            / "v2_0"
            / "research_benchmarks"
            / "raydb_style"
            / "rtdl_raydb_style_benchmark_app.py"
        ).read_text()

        self.assertIn("native_device_column_path_used = backend == \"optix\" and not allow_reference_fallback", source)
        self.assertIn("rt.run_generic_ray_triangle_hit_stream_device_columns_3d", source)
        self.assertIn("host_row_bridge_bypassed", source)
        self.assertIn("native_device_column_path_used", source)
        self.assertIn("same-pointer/no-host-stage pod evidence", source)


if __name__ == "__main__":
    unittest.main()
