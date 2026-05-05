from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt


class Goal1289V15GraphVisibilityGenericDispatchTest(unittest.TestCase):
    def _case(self):
        pairs = (
            (rt.Point(id=1, x=0.0, y=0.25), rt.Point(id=2, x=2.0, y=0.25)),
            (rt.Point(id=3, x=0.0, y=2.0), rt.Point(id=4, x=2.0, y=2.0)),
        )
        blockers = (
            rt.Triangle(id=10, x0=1.0, y0=0.0, x1=1.0, y1=1.0, x2=1.2, y2=0.5),
        )
        return pairs, blockers

    def test_cpu_visibility_pair_rows_use_generic_anyhit_surface(self) -> None:
        pairs, blockers = self._case()

        with mock.patch(
            "rtdsl.visibility_runtime.run_generic_ray_triangle_any_hit",
            wraps=rt.run_generic_ray_triangle_any_hit,
        ) as generic:
            rows = rt.visibility_pair_rows(pairs, blockers, backend="cpu")

        self.assertEqual(
            rows,
            (
                {"observer_id": 1, "target_id": 2, "visible": 0},
                {"observer_id": 3, "target_id": 4, "visible": 1},
            ),
        )
        generic.assert_called_once()

    def test_optix_visibility_pair_rows_delegate_to_generic_surface(self) -> None:
        pairs, blockers = self._case()

        with mock.patch(
            "rtdsl.visibility_runtime.run_generic_ray_triangle_any_hit",
            return_value=({"ray_id": 0, "any_hit": 1}, {"ray_id": 1, "any_hit": 0}),
        ) as generic:
            rows = rt.visibility_pair_rows(pairs, blockers, backend="optix")

        self.assertEqual(
            rows,
            (
                {"observer_id": 1, "target_id": 2, "visible": 0},
                {"observer_id": 3, "target_id": 4, "visible": 1},
            ),
        )
        self.assertEqual(generic.call_args.kwargs["backend"], "optix")

    def test_frozen_backend_dispatch_is_not_routed_through_generic_surface(self) -> None:
        pairs, blockers = self._case()

        with mock.patch("rtdsl.visibility_runtime.run_generic_ray_triangle_any_hit") as generic:
            with mock.patch(
                "rtdsl.vulkan_runtime.run_vulkan",
                return_value=({"ray_id": 0, "any_hit": 1}, {"ray_id": 1, "any_hit": 0}),
            ) as run_vulkan:
                rows = rt.visibility_pair_rows(pairs, blockers, backend="vulkan")

        self.assertEqual(rows[0]["visible"], 0)
        self.assertEqual(rows[1]["visible"], 1)
        generic.assert_not_called()
        run_vulkan.assert_called_once()


if __name__ == "__main__":
    unittest.main()
