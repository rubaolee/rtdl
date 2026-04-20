from __future__ import annotations

import platform
import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_2d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def _case_2d() -> dict[str, tuple[object, ...]]:
    return {
        "rays": (
            rt.Ray2D(id=1, ox=-1.0, oy=0.5, dx=1.0, dy=0.0, tmax=4.0),
            rt.Ray2D(id=2, ox=4.0, oy=4.0, dx=1.0, dy=0.0, tmax=1.0),
        ),
        "triangles": (
            rt.Triangle(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0, x2=0.0, y2=2.0),
            rt.Triangle(id=20, x0=10.0, y0=10.0, x1=11.0, y1=10.0, x2=10.0, y2=11.0),
        ),
    }


def _case_3d() -> dict[str, tuple[object, ...]]:
    return {
        "rays": (
            rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=0.0, dx=10.0, dy=0.0, dz=0.0, tmax=1.0),
            rt.Ray3D(id=2, ox=0.0, oy=2.0, oz=0.0, dx=10.0, dy=0.0, dz=0.0, tmax=1.0),
        ),
        "triangles": (
            rt.Triangle3D(id=20, x0=5.0, y0=-1.0, z0=-1.0, x1=5.0, y1=1.0, z1=-1.0, x2=5.0, y2=0.0, z2=1.0),
        ),
    }


def _available(probe) -> bool:
    try:
        probe()
        return True
    except Exception:
        return False


def _apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    return _available(rt.apple_rt_context_probe)


class Goal636BackendAnyHitDispatchTest(unittest.TestCase):
    @unittest.skipUnless(_available(rt.embree_version), "Embree backend is not available")
    def test_embree_any_hit_matches_cpu(self) -> None:
        case = _case_2d()
        expected = rt.run_cpu(ray_triangle_any_hit_2d_kernel, **case)

        self.assertEqual(rt.run_embree(ray_triangle_any_hit_2d_kernel, **case), expected)
        self.assertEqual(rt.prepare_embree(ray_triangle_any_hit_2d_kernel).run(**case), expected)

    @unittest.skipUnless(_available(rt.optix_version), "OptiX backend is not available")
    def test_optix_any_hit_matches_cpu(self) -> None:
        case = _case_2d()
        expected = rt.run_cpu(ray_triangle_any_hit_2d_kernel, **case)

        self.assertEqual(rt.run_optix(ray_triangle_any_hit_2d_kernel, **case), expected)

    @unittest.skipUnless(_available(rt.vulkan_version), "Vulkan backend is not available")
    def test_vulkan_any_hit_matches_cpu(self) -> None:
        case = _case_2d()
        expected = rt.run_cpu(ray_triangle_any_hit_2d_kernel, **case)

        self.assertEqual(rt.run_vulkan(ray_triangle_any_hit_2d_kernel, **case), expected)
        with self.assertRaisesRegex(ValueError, "raw mode is not supported"):
            rt.run_vulkan(ray_triangle_any_hit_2d_kernel, result_mode="raw", **case)

    @unittest.skipUnless(_available(rt.hiprt_context_probe), "HIPRT backend is not available")
    def test_hiprt_any_hit_matches_cpu_for_2d_and_3d(self) -> None:
        case_2d = _case_2d()
        case_3d = _case_3d()

        self.assertEqual(
            rt.run_hiprt(ray_triangle_any_hit_2d_kernel, **case_2d),
            rt.run_cpu(ray_triangle_any_hit_2d_kernel, **case_2d),
        )
        self.assertEqual(
            rt.run_hiprt(ray_triangle_any_hit_3d_kernel, **case_3d),
            rt.run_cpu(ray_triangle_any_hit_3d_kernel, **case_3d),
        )

    @unittest.skipUnless(_apple_rt_available(), "Apple RT backend is not available")
    def test_apple_rt_any_hit_native_only_matches_cpu_for_2d_and_3d(self) -> None:
        case_2d = _case_2d()
        case_3d = _case_3d()

        self.assertEqual(
            rt.run_apple_rt(ray_triangle_any_hit_2d_kernel, native_only=True, **case_2d),
            rt.run_cpu(ray_triangle_any_hit_2d_kernel, **case_2d),
        )
        self.assertEqual(
            rt.run_apple_rt(ray_triangle_any_hit_3d_kernel, native_only=True, **case_3d),
            rt.run_cpu(ray_triangle_any_hit_3d_kernel, **case_3d),
        )

    @unittest.skipUnless(_available(rt.embree_version), "Embree backend is not available")
    def test_visibility_rows_can_use_embree_backend_compatibility_dispatch(self) -> None:
        observers = (rt.Point(id=1, x=0.0, y=0.0),)
        targets = (rt.Point(id=2, x=2.0, y=0.0), rt.Point(id=3, x=0.0, y=2.0))
        blockers = (rt.Triangle(id=10, x0=0.9, y0=-0.5, x1=1.1, y1=0.5, x2=1.3, y2=-0.5),)

        self.assertEqual(
            rt.visibility_rows(observers, targets, blockers, backend="embree"),
            rt.visibility_rows_cpu(observers, targets, blockers),
        )

    @unittest.skipUnless(_apple_rt_available(), "Apple RT backend is not available")
    def test_visibility_rows_can_use_apple_rt_backend_compatibility_dispatch(self) -> None:
        observers = (rt.Point(id=1, x=0.0, y=0.0),)
        targets = (rt.Point(id=2, x=2.0, y=0.0), rt.Point(id=3, x=0.0, y=2.0))
        blockers = (rt.Triangle(id=10, x0=0.9, y0=-0.5, x1=1.1, y1=0.5, x2=1.3, y2=-0.5),)

        self.assertEqual(
            rt.visibility_rows(observers, targets, blockers, backend="apple_rt", native_only=True),
            rt.visibility_rows_cpu(observers, targets, blockers),
        )


if __name__ == "__main__":
    unittest.main()
