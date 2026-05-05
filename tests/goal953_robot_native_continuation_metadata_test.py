import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_robot_collision_screening_app as robot


class _FakeGenericPreparedCount:
    def __init__(self, count: int = 2):
        self.count = count

    def __call__(
        self,
        *,
        triangles,
        rays,
        backend: str,
        query_repeats: int = 1,
        prepare_scene=None,
        prepare_rays=None,
    ):
        return {
            "primitive": "ANY_HIT",
            "summary_primitive": "COUNT_HITS",
            "hit_count": self.count,
            "run_phases": {
                "scene_prepare_sec": 0.001,
                "ray_prepare_sec": 0.001,
                "query_anyhit_count_sec": 0.001,
            },
        }


class _FakePreparedScene:
    def __init__(self, count: int = 2, pose_flags=(False, True, True, False)):
        self.count_value = count
        self.pose_flags = tuple(pose_flags)

    def count(self, prepared_rays):
        return self.count_value

    def pose_flags_packed(self, prepared_rays, pose_indices, *, pose_count):
        return self.pose_flags[:pose_count]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


class _FakePreparedRays:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


class Goal953RobotNativeContinuationMetadataTest(unittest.TestCase):
    def test_prepared_count_reports_native_continuation(self) -> None:
        with mock.patch.object(
            robot.rt,
            "run_generic_prepared_ray_triangle_any_hit_count",
            side_effect=_FakeGenericPreparedCount(count=7),
        ):
            payload = robot.run_app("optix", optix_summary_mode="prepared_count")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_prepared_any_hit_count")
        self.assertEqual(payload["output_mode"], "hit_count")
        self.assertEqual(payload["prepared_summary"]["generic_primitive"], "ANY_HIT")
        self.assertEqual(payload["prepared_summary"]["summary_primitive"], "COUNT_HITS")
        self.assertTrue(payload["matches_oracle"])

    def test_prepared_pose_flags_reports_native_continuation(self) -> None:
        with (
            mock.patch.object(
                robot.rt,
                "prepare_optix_ray_triangle_any_hit_2d",
                return_value=_FakePreparedScene(pose_flags=(False, True, True, False)),
            ),
            mock.patch.object(robot.rt, "prepare_optix_rays_2d", return_value=_FakePreparedRays()),
        ):
            payload = robot.run_app("optix", optix_summary_mode="prepared_pose_flags")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_prepared_pose_flags")
        self.assertEqual(payload["output_mode"], "pose_flags")
        self.assertTrue(payload["matches_oracle"])

    def test_prepared_pose_flags_scaled_fixture_uses_analytic_validation(self) -> None:
        with (
            mock.patch(
                "examples.rtdl_robot_collision_screening_app.rt.ray_triangle_any_hit_cpu",
                side_effect=AssertionError("scaled prepared pose flags should not run CPU oracle"),
            ),
            mock.patch.object(
                robot.rt,
                "prepare_optix_ray_triangle_any_hit_2d",
                return_value=_FakePreparedScene(pose_flags=(False, True, False, True, False, True)),
            ),
            mock.patch.object(robot.rt, "prepare_optix_rays_2d", return_value=_FakePreparedRays()),
        ):
            payload = robot.run_app(
                "optix",
                optix_summary_mode="prepared_pose_flags",
                pose_count=6,
                obstacle_count=4,
            )

        self.assertEqual(payload["validation_mode"], "analytic_scaled_fixture")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["oracle_colliding_pose_ids"], [2, 4, 6])

    def test_prepared_count_can_skip_cpu_validation_for_timing(self) -> None:
        with (
            mock.patch(
                "examples.rtdl_robot_collision_screening_app.rt.ray_triangle_any_hit_cpu",
                side_effect=AssertionError("skip_validation should not run CPU oracle"),
            ),
            mock.patch.object(
                robot.rt,
                "run_generic_prepared_ray_triangle_any_hit_count",
                side_effect=_FakeGenericPreparedCount(count=7),
            ),
        ):
            payload = robot.run_app("optix", optix_summary_mode="prepared_count", skip_validation=True)

        self.assertEqual(payload["validation_mode"], "skipped")
        self.assertIsNone(payload["oracle_hit_edge_count"])
        self.assertIsNone(payload["matches_oracle"])

    def test_row_mode_compact_outputs_do_not_overstate_native_continuation(self) -> None:
        for output_mode in ("full", "pose_flags", "hit_count"):
            with self.subTest(output_mode=output_mode):
                payload = robot.run_app("cpu_python_reference", output_mode=output_mode)
                self.assertFalse(payload["native_continuation_active"])
                self.assertEqual(payload["native_continuation_backend"], "none")
                self.assertTrue(payload["matches_oracle"])


if __name__ == "__main__":
    unittest.main()
