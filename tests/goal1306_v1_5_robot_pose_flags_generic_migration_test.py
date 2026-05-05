from __future__ import annotations

import unittest

import rtdsl as rt
from examples import rtdl_robot_collision_screening_app as robot


class _PreparedScene:
    def __init__(self, flags: tuple[bool, ...]) -> None:
        self.flags = flags
        self.query_count = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def pose_flags_packed(self, _rays, _group_indices, *, pose_count: int) -> tuple[bool, ...]:
        self.query_count += 1
        return self.flags[:pose_count]


class _PreparedRays:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass


class Goal1306V15RobotPoseFlagsGenericMigrationTest(unittest.TestCase):
    def test_generic_grouped_count_threshold_bool_metadata(self) -> None:
        prepared_scene = _PreparedScene((True, False, True))

        result = rt.run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool(
            triangles=("triangles",),
            rays=("rays",),
            group_indices=(0, 0, 1, 2),
            group_count=3,
            backend="optix",
            query_repeats=2,
            prepare_scene=lambda _triangles: prepared_scene,
            prepare_rays=lambda _rays: _PreparedRays(),
            prepare_group_indices=None,
        )

        self.assertEqual(result["primitive"], "ANY_HIT")
        self.assertEqual(result["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(result["result_layout"], "grouped_threshold_bool")
        self.assertEqual(result["group_flags"], (True, False, True))
        self.assertEqual(result["threshold_reached_count"], 2)
        self.assertEqual(prepared_scene.query_count, 2)

    def test_robot_prepared_pose_flags_uses_generic_metadata(self) -> None:
        original = robot.rt.run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool

        def fake_generic_pose_flags(**_kwargs):
            return {
                "primitive": "ANY_HIT",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "result_layout": "grouped_threshold_bool",
                "group_flags": (False, True, False, True),
                "threshold_reached_count": 2,
                "run_phases": {"query_grouped_count_threshold_bool_sec": 0.0},
            }

        robot.rt.run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool = fake_generic_pose_flags
        try:
            payload = robot.run_app(
                backend="optix",
                optix_summary_mode="prepared_pose_flags",
                pose_count=4,
                obstacle_count=4,
            )
        finally:
            robot.rt.run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool = original

        self.assertEqual(payload["prepared_summary"]["generic_primitive"], "ANY_HIT")
        self.assertEqual(payload["prepared_summary"]["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(payload["prepared_summary"]["result_layout"], "grouped_threshold_bool")
        self.assertEqual(payload["native_continuation_backend"], "optix_prepared_pose_flags")
        self.assertTrue(payload["matches_oracle"])

    def test_grouped_count_threshold_bool_rejects_non_one_threshold(self) -> None:
        with self.assertRaisesRegex(ValueError, "threshold=1"):
            rt.run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool(
                triangles=(),
                rays=(),
                group_indices=(),
                group_count=0,
                backend="optix",
                threshold=2,
                prepare_scene=lambda _triangles: _PreparedScene(()),
                prepare_rays=lambda _rays: _PreparedRays(),
                prepare_group_indices=None,
            )


if __name__ == "__main__":
    unittest.main()
