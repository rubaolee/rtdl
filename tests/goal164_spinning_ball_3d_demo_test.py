import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.embree_runtime import _call_ray_hitcount_embree_packed
from rtdsl.embree_runtime import _pack_for_geometry as _pack_for_geometry_embree
from rtdsl.embree_runtime import PackedRays as _PackedRays
from rtdsl.embree_runtime import PackedTriangles as _PackedTriangles
from rtdsl.optix_runtime import _call_ray_hitcount_optix_packed
from rtdsl.optix_runtime import _pack_for_geometry as _pack_for_geometry_optix
from examples.rtdl_spinning_ball_3d_demo import _run_backend_rows
from examples.rtdl_spinning_ball_3d_demo import make_camera_rays
from examples.rtdl_spinning_ball_3d_demo import make_uv_sphere_mesh
from examples.rtdl_spinning_ball_3d_demo import ray_triangle_hitcount_3d_demo
from examples.rtdl_spinning_ball_3d_demo import render_spinning_ball_3d_frames
from rtdsl.vulkan_runtime import _call_ray_hitcount_vulkan_packed
from rtdsl.vulkan_runtime import _pack_for_geometry as _pack_for_geometry_vulkan


class _SymbolProbe(RuntimeError):
    def __init__(self, symbol_name: str) -> None:
        super().__init__(symbol_name)
        self.symbol_name = symbol_name


class _ProbeCallable:
    def __init__(self, symbol_name: str) -> None:
        self.symbol_name = symbol_name

    def __call__(self, *args, **kwargs):
        raise _SymbolProbe(self.symbol_name)


class _ProbeLibrary:
    def __init__(self, **symbols) -> None:
        self._symbols = symbols

    def __getattr__(self, name: str):
        if name in self._symbols:
            return self._symbols[name]
        raise AttributeError(name)


class Goal164SpinningBall3DDemoTest(unittest.TestCase):
    def test_3d_backend_packers_preserve_dimension_for_empty_payloads(self) -> None:
        rays_input = SimpleNamespace(geometry=SimpleNamespace(name="rays"), layout=rt.Ray3DLayout)
        triangles_input = SimpleNamespace(geometry=SimpleNamespace(name="triangles"), layout=rt.Triangle3DLayout)

        embree_rays = _pack_for_geometry_embree(rays_input, ())
        embree_triangles = _pack_for_geometry_embree(triangles_input, ())
        optix_rays = _pack_for_geometry_optix(rays_input, ())
        optix_triangles = _pack_for_geometry_optix(triangles_input, ())
        vulkan_rays = _pack_for_geometry_vulkan(rays_input, ())
        vulkan_triangles = _pack_for_geometry_vulkan(triangles_input, ())

        self.assertEqual((embree_rays.dimension, embree_triangles.dimension), (3, 3))
        self.assertEqual((optix_rays.dimension, optix_triangles.dimension), (3, 3))
        self.assertEqual((vulkan_rays.dimension, vulkan_triangles.dimension), (3, 3))
        self.assertEqual((embree_rays.count, embree_triangles.count), (0, 0))
        self.assertEqual((optix_rays.count, optix_triangles.count), (0, 0))
        self.assertEqual((vulkan_rays.count, vulkan_triangles.count), (0, 0))

    def _backend_rows_or_skip(self, backend: str, *, rays, triangles):
        try:
            return _run_backend_rows(backend, rays=rays, triangles=triangles)
        except (RuntimeError, OSError, ValueError) as exc:
            self.skipTest(f"{backend} unavailable for Goal 164 3D parity test: {exc}")

    def _assert_backend_matches_reference(self, backend: str, *, rays, triangles) -> None:
        reference_rows = self._backend_rows_or_skip(
            "cpu_python_reference",
            rays=rays,
            triangles=triangles,
        )
        backend_rows = self._backend_rows_or_skip(
            backend,
            rays=rays,
            triangles=triangles,
        )
        self.assertEqual(
            backend_rows,
            reference_rows,
            msg=f"{backend} 3D ray rows drift from cpu_python_reference",
        )

    def test_3d_ray_triangle_reference_counts_match_simple_case(self) -> None:
        rays = (
            rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=2.0, dx=0.0, dy=0.0, dz=-1.0, tmax=5.0),
            rt.Ray3D(id=2, ox=3.0, oy=3.0, oz=2.0, dx=0.0, dy=0.0, dz=-1.0, tmax=5.0),
        )
        triangles = (
            rt.Triangle3D(
                id=10,
                x0=-1.0,
                y0=-1.0,
                z0=0.0,
                x1=1.0,
                y1=-1.0,
                z1=0.0,
                x2=0.0,
                y2=1.0,
                z2=0.0,
            ),
        )

        rows = rt.run_cpu_python_reference(ray_triangle_hitcount_3d_demo, rays=rays, triangles=triangles)
        self.assertEqual(rows, ({"ray_id": 1, "hit_count": 1}, {"ray_id": 2, "hit_count": 0}))

    def test_3d_backend_dispatch_uses_3d_symbols(self) -> None:
        rays = _PackedRays(records=object(), count=1, dimension=3)
        triangles = _PackedTriangles(records=object(), count=1, dimension=3)
        packed_inputs = {"rays": rays, "triangles": triangles}
        compiled = SimpleNamespace(
            candidates=SimpleNamespace(
                left=SimpleNamespace(name="rays"),
                right=SimpleNamespace(name="triangles"),
            )
        )

        with self.assertRaises(_SymbolProbe) as embree_probe:
            _call_ray_hitcount_embree_packed(
                compiled,
                packed_inputs,
                _ProbeLibrary(
                    rtdl_embree_run_ray_hitcount=_ProbeCallable("embree-2d"),
                    rtdl_embree_run_ray_hitcount_3d=_ProbeCallable("embree-3d"),
                ),
            )
        self.assertEqual(embree_probe.exception.symbol_name, "embree-3d")

        with self.assertRaises(_SymbolProbe) as optix_probe:
            _call_ray_hitcount_optix_packed(
                compiled,
                packed_inputs,
                _ProbeLibrary(
                    rtdl_optix_run_ray_hitcount=_ProbeCallable("optix-2d"),
                    rtdl_optix_run_ray_hitcount_3d=_ProbeCallable("optix-3d"),
                ),
            )
        self.assertEqual(optix_probe.exception.symbol_name, "optix-3d")

        with self.assertRaises(_SymbolProbe) as vulkan_probe:
            _call_ray_hitcount_vulkan_packed(
                compiled,
                packed_inputs,
                _ProbeLibrary(
                    rtdl_vulkan_run_ray_hitcount=_ProbeCallable("vulkan-2d"),
                    rtdl_vulkan_run_ray_hitcount_3d=_ProbeCallable("vulkan-3d"),
                ),
            )
        self.assertEqual(vulkan_probe.exception.symbol_name, "vulkan-3d")

    def test_3d_backend_matrix_matches_reference_for_simple_scene(self) -> None:
        rays = (
            rt.Ray3D(id=1, ox=0.0, oy=0.0, oz=2.0, dx=0.0, dy=0.0, dz=-1.0, tmax=5.0),
            rt.Ray3D(id=2, ox=3.0, oy=3.0, oz=2.0, dx=0.0, dy=0.0, dz=-1.0, tmax=5.0),
        )
        triangles = (
            rt.Triangle3D(
                id=10,
                x0=-1.0,
                y0=-1.0,
                z0=0.0,
                x1=1.0,
                y1=-1.0,
                z1=0.0,
                x2=0.0,
                y2=1.0,
                z2=0.0,
            ),
        )
        for backend in ("embree", "optix", "vulkan"):
            with self.subTest(backend=backend):
                self._assert_backend_matches_reference(backend, rays=rays, triangles=triangles)

    def test_3d_backend_matrix_matches_reference_for_medium_sphere_scene(self) -> None:
        triangles = make_uv_sphere_mesh(
            latitude_bands=6,
            longitude_bands=12,
            radius=1.35,
            center=(0.0, 0.0, 0.0),
        )
        rays = make_camera_rays(
            width=18,
            height=18,
            eye=(0.0, 0.0, 5.4),
            target=(0.0, 0.0, 0.0),
            up_hint=(0.0, 1.0, 0.0),
            fov_y_degrees=34.0,
        )
        for backend in ("embree", "optix", "vulkan"):
            with self.subTest(backend=backend):
                self._assert_backend_matches_reference(backend, rays=rays, triangles=triangles)

    def test_3d_backend_matrix_matches_reference_for_demo_scene_pack(self) -> None:
        triangles = make_uv_sphere_mesh(
            latitude_bands=10,
            longitude_bands=20,
            radius=1.35,
            center=(0.0, 0.0, 0.0),
        )
        rays = make_camera_rays(
            width=48,
            height=48,
            eye=(0.0, 0.0, 5.4),
            target=(0.0, 0.0, 0.0),
            up_hint=(0.0, 1.0, 0.0),
            fov_y_degrees=34.0,
        )
        for backend in ("embree", "optix", "vulkan"):
            with self.subTest(backend=backend):
                self._assert_backend_matches_reference(backend, rays=rays, triangles=triangles)

    def test_render_spinning_ball_3d_frames_writes_frame_sequence(self) -> None:
        output_dir = Path("build/goal164_spinning_ball_3d_demo_test")
        summary = render_spinning_ball_3d_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=40,
            height=40,
            latitude_bands=10,
            longitude_bands=20,
            frame_count=3,
            output_dir=output_dir,
        )

        self.assertEqual(summary["frame_count"], 3)
        self.assertEqual(summary["image_width"], 40)
        self.assertEqual(summary["image_height"], 40)
        self.assertGreater(summary["triangle_count"], 0)
        self.assertGreater(summary["total_query_seconds"], 0.0)
        self.assertGreater(summary["total_shading_seconds"], 0.0)
        self.assertGreater(summary["query_share"], 0.0)

        frame_paths = []
        for frame in summary["frames"]:
            frame_path = Path(frame["frame_path"])
            self.assertTrue(frame_path.exists())
            self.assertGreater(frame["rt_rows"], 0)
            self.assertGreater(frame["hit_pixels"], 0)
            frame_paths.append(frame_path)

        with frame_paths[0].open("rb") as handle:
            header = handle.readline().decode("ascii").strip()
            dims = handle.readline().decode("ascii").strip()
            max_value = handle.readline().decode("ascii").strip()
        self.assertEqual(header, "P6")
        self.assertEqual(dims, "40 40")
        self.assertEqual(max_value, "255")

        summary_path = output_dir / "summary.json"
        self.assertTrue(summary_path.exists())
        persisted = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["frame_count"], 3)
        self.assertEqual(len(persisted["frames"]), 3)


if __name__ == "__main__":
    unittest.main()
