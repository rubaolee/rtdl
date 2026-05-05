from __future__ import annotations

import unittest

import rtdsl as rt


class _PreparedScene:
    def __init__(self, count: int) -> None:
        self.count_value = count
        self.query_count = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def count(self, _rays) -> int:
        self.query_count += 1
        return self.count_value


class _PreparedRays:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass


class Goal1290V15GenericPreparedAnyHitCountTest(unittest.TestCase):
    def test_generic_prepared_optix_count_repeats_queries(self) -> None:
        prepared_scene = _PreparedScene(7)

        result = rt.run_generic_prepared_ray_triangle_any_hit_count(
            triangles=("triangles",),
            rays=("rays",),
            backend="optix",
            query_repeats=3,
            prepare_scene=lambda _triangles: prepared_scene,
            prepare_rays=lambda _rays: _PreparedRays(),
        )

        self.assertEqual(result["primitive"], "ANY_HIT")
        self.assertEqual(result["summary_primitive"], "COUNT_HITS")
        self.assertEqual(result["backend"], "optix")
        self.assertTrue(result["prepared"])
        self.assertEqual(result["query_repeats"], 3)
        self.assertEqual(result["hit_count"], 7)
        self.assertEqual(prepared_scene.query_count, 3)
        self.assertIn("query_anyhit_count_mean_sec", result["run_phases"])

    def test_graph_compatibility_wrapper_delegates_to_generic_prepared_count(self) -> None:
        prepared_scene = _PreparedScene(4)

        result = rt.run_prepared_visibility_anyhit_count(
            blockers=("blockers",),
            rays=("rays",),
            prepare_scene=lambda _blockers: prepared_scene,
            prepare_rays=lambda _rays: _PreparedRays(),
            visibility_query_repeats=2,
        )

        self.assertEqual(result["blocked_count"], 4)
        self.assertEqual(prepared_scene.query_count, 2)
        self.assertIn("query_anyhit_count_min_sec", result["run_phases"])

    def test_generic_prepared_count_rejects_non_positive_repeats(self) -> None:
        with self.assertRaisesRegex(ValueError, "query_repeats must be positive"):
            rt.run_generic_prepared_ray_triangle_any_hit_count(
                triangles=(),
                rays=(),
                backend="optix",
                query_repeats=0,
                prepare_scene=lambda _triangles: _PreparedScene(0),
                prepare_rays=lambda _rays: _PreparedRays(),
            )

    def test_generic_prepared_count_rejects_frozen_backends(self) -> None:
        for backend in ("vulkan", "hiprt", "apple_rt"):
            with self.subTest(backend=backend):
                with self.assertRaisesRegex(ValueError, "frozen before v2.1"):
                    rt.run_generic_prepared_ray_triangle_any_hit_count(
                        triangles=(),
                        rays=(),
                        backend=backend,
                        prepare_scene=lambda _triangles: _PreparedScene(0),
                        prepare_rays=lambda _rays: _PreparedRays(),
                    )


if __name__ == "__main__":
    unittest.main()
