from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt
from rtdsl.datasets import parse_cdb_text
from rtdsl import embree_runtime
from rtdsl import optix_runtime
from rtdsl import vulkan_runtime
from rtdsl.reference import Point
from rtdsl.reference import Polygon


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_counties_positive_hits():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    refined = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(boundary_mode="inclusive", result_mode="positive_hits"),
    )
    return rt.emit(refined, fields=["point_id", "polygon_id", "contains"])


POINTS = (
    Point(id=1, x=0.25, y=0.25),
    Point(id=2, x=1.25, y=1.25),
)

POLYGONS = (
    Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
)


class _FakePreparedExecution:
    def run(self):
        return ({"ok": True},)

    def run_raw(self):
        return self


class _FakePreparedKernel:
    def bind(self, **inputs):
        return _FakePreparedExecution()


class Goal80RuntimeIdentityFastPathTest(unittest.TestCase):
    def setUp(self) -> None:
        embree_runtime.clear_embree_prepared_cache()
        optix_runtime.clear_optix_prepared_cache()
        vulkan_runtime.clear_vulkan_prepared_cache()
        self.compiled = rt.compile_kernel(point_in_counties_positive_hits)

    def test_embree_identity_fast_path_skips_normalize_on_repeated_tuple_inputs(self) -> None:
        with mock.patch.object(embree_runtime, "prepare_embree", return_value=_FakePreparedKernel()), mock.patch.object(
            embree_runtime,
            "_normalize_records",
            side_effect=AssertionError("Embree normalize should not run for canonical tuple fast path"),
        ):
            first = embree_runtime.run_embree(self.compiled, points=POINTS, polygons=POLYGONS)
            second = embree_runtime.run_embree(self.compiled, points=POINTS, polygons=POLYGONS)
        self.assertEqual(first, second)

    def test_optix_identity_fast_path_skips_normalize_on_repeated_tuple_inputs(self) -> None:
        with mock.patch.object(optix_runtime, "prepare_optix", return_value=_FakePreparedKernel()), mock.patch.object(
            optix_runtime,
            "_normalize_records",
            side_effect=AssertionError("OptiX normalize should not run for canonical tuple fast path"),
        ):
            first = optix_runtime.run_optix(self.compiled, points=POINTS, polygons=POLYGONS)
            second = optix_runtime.run_optix(self.compiled, points=POINTS, polygons=POLYGONS)
        self.assertEqual(first, second)

    def test_vulkan_identity_fast_path_skips_normalize_on_repeated_tuple_inputs(self) -> None:
        with mock.patch.object(vulkan_runtime, "prepare_vulkan", return_value=_FakePreparedKernel()), mock.patch.object(
            vulkan_runtime,
            "_normalize_records",
            side_effect=AssertionError("Vulkan normalize should not run for canonical tuple fast path"),
        ):
            first = vulkan_runtime.run_vulkan(self.compiled, points=POINTS, polygons=POLYGONS)
            second = vulkan_runtime.run_vulkan(self.compiled, points=POINTS, polygons=POLYGONS)
        self.assertEqual(first, second)

    def test_cdb_views_prime_packed_inputs_for_optix_bind(self) -> None:
        county = parse_cdb_text(
            "\n".join(
                [
                    "10 4 1 4 0 7",
                    "0 0",
                    "2 0",
                    "2 2",
                    "0 0",
                ]
            ),
            name="county",
        )
        zipcode = parse_cdb_text(
            "\n".join(
                [
                    "1 1 1 1 0 0",
                    "0.5 0.5",
                    "2 1 2 2 0 0",
                    "5.0 5.0",
                ]
            ),
            name="zipcode",
        )
        points = rt.chains_to_probe_points(zipcode)
        polygons = rt.chains_to_polygons(county)
        self.assertTrue(hasattr(points, "_rtdl_packed_points"))
        self.assertTrue(hasattr(polygons, "_rtdl_packed_polygons"))

        with mock.patch.object(optix_runtime, "prepare_optix", return_value=_FakePreparedKernel()), mock.patch.object(
            optix_runtime,
            "pack_points",
            side_effect=AssertionError("OptiX pack_points should reuse primed packed points"),
        ), mock.patch.object(
            optix_runtime,
            "pack_polygons",
            side_effect=AssertionError("OptiX pack_polygons should reuse primed packed polygons"),
        ):
            rows = optix_runtime.run_optix(self.compiled, points=points, polygons=polygons)
        self.assertEqual(rows, ({"ok": True},))

    def test_cdb_views_prime_packed_inputs_for_vulkan_bind(self) -> None:
        county = parse_cdb_text(
            "\n".join(
                [
                    "10 4 1 4 0 7",
                    "0 0",
                    "2 0",
                    "2 2",
                    "0 0",
                ]
            ),
            name="county",
        )
        zipcode = parse_cdb_text(
            "\n".join(
                [
                    "1 1 1 1 0 0",
                    "0.5 0.5",
                    "2 1 2 2 0 0",
                    "5.0 5.0",
                ]
            ),
            name="zipcode",
        )
        points = rt.chains_to_probe_points(zipcode)
        polygons = rt.chains_to_polygons(county)
        self.assertTrue(hasattr(points, "_rtdl_packed_points"))
        self.assertTrue(hasattr(polygons, "_rtdl_packed_polygons"))

        with mock.patch.object(vulkan_runtime, "prepare_vulkan", return_value=_FakePreparedKernel()), mock.patch.object(
            embree_runtime,
            "pack_points",
            side_effect=AssertionError("Vulkan pack_points should reuse primed packed points"),
        ), mock.patch.object(
            embree_runtime,
            "pack_polygons",
            side_effect=AssertionError("Vulkan pack_polygons should reuse primed packed polygons"),
        ):
            rows = vulkan_runtime.run_vulkan(self.compiled, points=points, polygons=polygons)
        self.assertEqual(rows, ({"ok": True},))


if __name__ == "__main__":
    unittest.main()
