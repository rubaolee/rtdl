from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt


class Goal1288V15GenericAnyHitCountTest(unittest.TestCase):
    def _case(self):
        rays = (
            rt.Ray2D(id=0, ox=0.0, oy=0.25, dx=2.0, dy=0.0, tmax=1.0),
            rt.Ray2D(id=1, ox=0.0, oy=2.0, dx=2.0, dy=0.0, tmax=1.0),
        )
        triangles = (
            rt.Triangle(id=10, x0=1.0, y0=0.0, x1=1.0, y1=1.0, x2=1.2, y2=0.5),
        )
        return rays, triangles

    def test_cpu_generic_anyhit_rows_are_app_name_free(self) -> None:
        rays, triangles = self._case()

        rows = rt.run_generic_ray_triangle_any_hit(rays, triangles, backend="cpu")

        self.assertEqual(rows, ({"ray_id": 0, "any_hit": 1}, {"ray_id": 1, "any_hit": 0}))

    def test_cpu_generic_count_hits_summary(self) -> None:
        rays, triangles = self._case()

        summary = rt.run_generic_ray_triangle_any_hit_count(
            rays,
            triangles,
            backend="cpu_python_reference",
            include_rows=True,
        )

        self.assertEqual(summary["primitive"], "ANY_HIT")
        self.assertEqual(summary["summary_primitive"], "COUNT_HITS")
        self.assertEqual(summary["backend"], "cpu")
        self.assertFalse(summary["active_v1_5_backend"])
        self.assertEqual(summary["row_count"], 2)
        self.assertEqual(summary["hit_count"], 1)
        self.assertEqual(summary["scalar_reduction"]["summary_primitive"], "COUNT_HITS")
        self.assertEqual(summary["scalar_reduction"]["result_layout"], "scalar_int64_hit_count")
        self.assertEqual(summary["scalar_reduction"]["dtype"], "int64")
        self.assertEqual(summary["scalar_reduction"]["input_field"], "any_hit")
        self.assertIn("not native backend acceleration", summary["scalar_reduction"]["claim_boundary"])
        self.assertEqual(summary["rows"], ({"ray_id": 0, "any_hit": 1}, {"ray_id": 1, "any_hit": 0}))

    def test_generic_count_hits_summary_uses_scalar_reduction_surface(self) -> None:
        rays, triangles = self._case()

        with mock.patch(
            "rtdsl.generic_primitives.run_generic_scalar_reduction",
            wraps=rt.run_generic_scalar_reduction,
        ) as scalar_reduction:
            summary = rt.run_generic_ray_triangle_any_hit_count(rays, triangles, backend="cpu")

        scalar_reduction.assert_called_once_with(
            ({"ray_id": 0, "any_hit": 1}, {"ray_id": 1, "any_hit": 0}),
            summary_primitive="COUNT_HITS",
        )
        self.assertEqual(summary["hit_count"], 1)

    def test_empty_build_returns_zero_rows_without_backend_dispatch(self) -> None:
        rays, _triangles = self._case()

        with mock.patch("rtdsl.optix_runtime.run_optix") as run_optix:
            rows = rt.run_generic_ray_triangle_any_hit(rays, (), backend="optix")

        self.assertEqual(rows, ({"ray_id": 0, "any_hit": 0}, {"ray_id": 1, "any_hit": 0}))
        run_optix.assert_not_called()

    def test_optix_dispatch_is_available_for_active_v1_5_backend(self) -> None:
        rays, triangles = self._case()

        with mock.patch(
            "rtdsl.optix_runtime.run_optix",
            return_value=({"ray_id": "0", "any_hit": "1"}, {"ray_id": "1", "any_hit": "0"}),
        ) as run_optix:
            rows = rt.run_generic_ray_triangle_any_hit(rays, triangles, backend="optix")

        self.assertEqual(rows, ({"ray_id": 0, "any_hit": 1}, {"ray_id": 1, "any_hit": 0}))
        run_optix.assert_called_once()

    def test_frozen_backends_are_rejected_for_v1_5_generic_primitives(self) -> None:
        rays, triangles = self._case()

        for backend in ("vulkan", "hiprt", "apple_rt"):
            with self.subTest(backend=backend):
                with self.assertRaisesRegex(ValueError, "frozen before v2.1"):
                    rt.run_generic_ray_triangle_any_hit(rays, triangles, backend=backend)


if __name__ == "__main__":
    unittest.main()
