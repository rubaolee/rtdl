from __future__ import annotations

import unittest

import rtdsl as rt


class _PreparedScene:
    enter_count = 0
    exit_count = 0

    def __init__(self, count: int) -> None:
        self.count_value = count
        self.query_count = 0

    def __enter__(self):
        type(self).enter_count += 1
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        type(self).exit_count += 1

    def count(self, _rays) -> int:
        self.query_count += 1
        return self.count_value


class _PreparedRays:
    enter_count = 0

    def __enter__(self):
        type(self).enter_count += 1
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass


class Goal1295V15GenericPreparedSceneSessionTest(unittest.TestCase):
    def setUp(self) -> None:
        _PreparedScene.enter_count = 0
        _PreparedScene.exit_count = 0
        _PreparedRays.enter_count = 0

    def test_reusable_prepared_scene_amortizes_scene_prepare_across_ray_batches(self) -> None:
        prepared_scene = _PreparedScene(5)

        with rt.prepare_generic_ray_triangle_any_hit_scene(
            triangles=("triangles",),
            backend="optix",
            prepare_scene=lambda _triangles: prepared_scene,
            prepare_rays=lambda _rays: _PreparedRays(),
        ) as session:
            first = session.count(("rays-a",), query_repeats=2)
            second = session.count(("rays-b",), query_repeats=3)

        self.assertEqual(_PreparedScene.enter_count, 1)
        self.assertEqual(_PreparedScene.exit_count, 1)
        self.assertEqual(_PreparedRays.enter_count, 2)
        self.assertEqual(prepared_scene.query_count, 5)
        self.assertEqual(first["hit_count"], 5)
        self.assertEqual(second["hit_count"], 5)
        self.assertEqual(first["query_batch_index"], 1)
        self.assertEqual(second["query_batch_index"], 2)
        self.assertTrue(first["scene_reusable"])
        self.assertEqual(first["run_phases"]["scene_prepare_sec_this_batch"], 0.0)
        self.assertEqual(second["run_phases"]["scene_prepare_sec"], first["run_phases"]["scene_prepare_sec"])

    def test_one_shot_prepared_count_still_uses_session_contract(self) -> None:
        prepared_scene = _PreparedScene(7)

        result = rt.run_generic_prepared_ray_triangle_any_hit_count(
            triangles=("triangles",),
            rays=("rays",),
            backend="optix",
            query_repeats=4,
            prepare_scene=lambda _triangles: prepared_scene,
            prepare_rays=lambda _rays: _PreparedRays(),
        )

        self.assertEqual(result["hit_count"], 7)
        self.assertEqual(result["query_repeats"], 4)
        self.assertEqual(result["query_batch_index"], 1)
        self.assertTrue(result["scene_reusable"])
        self.assertEqual(prepared_scene.query_count, 4)
        self.assertEqual(_PreparedScene.enter_count, 1)
        self.assertEqual(_PreparedScene.exit_count, 1)

    def test_session_rejects_closed_queries(self) -> None:
        session = rt.prepare_generic_ray_triangle_any_hit_scene(
            triangles=("triangles",),
            backend="optix",
            prepare_scene=lambda _triangles: _PreparedScene(1),
            prepare_rays=lambda _rays: _PreparedRays(),
        )
        session.close()

        with self.assertRaisesRegex(RuntimeError, "closed"):
            session.count(("rays",))

    def test_one_shot_rejects_bad_repeats_before_scene_prepare(self) -> None:
        def fail_prepare(_triangles):
            raise AssertionError("scene should not be prepared")

        with self.assertRaisesRegex(ValueError, "query_repeats must be positive"):
            rt.run_generic_prepared_ray_triangle_any_hit_count(
                triangles=("triangles",),
                rays=("rays",),
                backend="optix",
                query_repeats=0,
                prepare_scene=fail_prepare,
                prepare_rays=lambda _rays: _PreparedRays(),
            )

    def test_session_rejects_frozen_backends(self) -> None:
        for backend in ("vulkan", "hiprt", "apple_rt"):
            with self.subTest(backend=backend):
                with self.assertRaisesRegex(ValueError, "frozen before v2.1"):
                    rt.prepare_generic_ray_triangle_any_hit_scene(
                        triangles=(),
                        backend=backend,
                        prepare_scene=lambda _triangles: _PreparedScene(0),
                        prepare_rays=lambda _rays: _PreparedRays(),
                    )


if __name__ == "__main__":
    unittest.main()
