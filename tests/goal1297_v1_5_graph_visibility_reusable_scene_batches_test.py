import unittest
from unittest import mock

from examples import rtdl_graph_analytics_app


class Goal1297GraphVisibilityReusableSceneBatchesTest(unittest.TestCase):
    def test_optix_visibility_summary_reuses_generic_scene_across_ray_batches(self) -> None:
        class FakePreparedScene:
            scene_prepare_sec = 0.25

            def __init__(self):
                self.count_calls = 0
                self.closed = False

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                self.closed = True
                return None

            def count(self, rays, *, query_repeats=1, prepare_rays=None):
                self.count_calls += 1
                if isinstance(rays, tuple):
                    ray_count = len(rays)
                else:
                    ray_count_value = getattr(rays, "count", len(rays) if hasattr(rays, "__len__") else 0)
                    ray_count = ray_count_value() if callable(ray_count_value) else ray_count_value
                return {
                    "hit_count": int(ray_count * 3 / 4),
                    "run_phases": {
                        "scene_prepare_sec": self.scene_prepare_sec,
                        "scene_prepare_sec_this_batch": 0.0,
                        "ray_prepare_sec": 0.01,
                        "query_anyhit_count_sec": 0.02 * query_repeats,
                        "query_anyhit_count_first_sec": 0.02,
                        "query_anyhit_count_mean_sec": 0.02,
                        "query_anyhit_count_min_sec": 0.01,
                    },
                }

        prepared_scene = FakePreparedScene()
        with (
            mock.patch.object(
                rtdl_graph_analytics_app.rt,
                "prepare_generic_ray_triangle_any_hit_scene",
                return_value=prepared_scene,
            ) as prepare_generic_scene,
            mock.patch.object(
                rtdl_graph_analytics_app.rt,
                "run_prepared_visibility_anyhit_count",
                side_effect=AssertionError("batched path must use the generic prepared scene session"),
            ),
        ):
            payload = rtdl_graph_analytics_app.run_app(
                "optix",
                "visibility_edges",
                copies=4,
                output_mode="summary",
                visibility_query_repeats=3,
                visibility_ray_batches=2,
                require_rt_core=True,
            )

        section = payload["sections"]["visibility_edges"]
        self.assertEqual(section["row_count"], 16)
        self.assertEqual(section["summary"], {"visible_edge_count": 4, "blocked_edge_count": 12})
        self.assertEqual(section["visibility_query_repeats"], 3)
        self.assertEqual(section["visibility_ray_batches"], 2)
        self.assertTrue(section["prepared_scene_reused_across_ray_batches"])
        self.assertEqual(section["native_continuation_backend"], "optix_reusable_prepared_visibility_anyhit_count")
        self.assertEqual(prepared_scene.count_calls, 2)
        self.assertTrue(prepared_scene.closed)
        prepare_generic_scene.assert_called_once()
        self.assertEqual(len(section["ray_batch_summaries"]), 2)
        self.assertEqual([batch["copies"] for batch in section["ray_batch_summaries"]], [2, 2])
        self.assertEqual([batch["ray_count"] for batch in section["ray_batch_summaries"]], [8, 8])
        self.assertEqual([batch["blocked_count"] for batch in section["ray_batch_summaries"]], [6, 6])
        self.assertGreaterEqual(section["run_phases"]["scene_prepare_sec"], 0.0)
        self.assertGreaterEqual(section["run_phases"]["ray_pack_sec"], 0.0)
        self.assertAlmostEqual(section["run_phases"]["ray_prepare_sec"], 0.02)
        self.assertAlmostEqual(section["run_phases"]["query_anyhit_count_sec"], 0.12)
        self.assertAlmostEqual(section["run_phases"]["query_anyhit_count_mean_sec"], 0.02)
        self.assertAlmostEqual(section["run_phases"]["query_anyhit_count_min_sec"], 0.01)

    def test_visibility_ray_batches_are_limited_to_optix_visibility_summary(self) -> None:
        with self.assertRaisesRegex(ValueError, "visibility_ray_batches is only supported"):
            rtdl_graph_analytics_app.run_app(
                "embree",
                "visibility_edges",
                copies=1,
                output_mode="summary",
                visibility_ray_batches=2,
            )

    def test_visibility_ray_batches_must_be_positive(self) -> None:
        with self.assertRaisesRegex(ValueError, "visibility_ray_batches must be positive"):
            rtdl_graph_analytics_app.run_app(
                "optix",
                "visibility_edges",
                copies=1,
                output_mode="summary",
                visibility_ray_batches=0,
            )


if __name__ == "__main__":
    unittest.main()
