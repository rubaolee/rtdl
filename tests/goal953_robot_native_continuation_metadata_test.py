import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_robot_collision_screening_app as robot


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
        with (
            mock.patch.object(robot.rt, "prepare_optix_ray_triangle_any_hit_2d", return_value=_FakePreparedScene(count=7)),
            mock.patch.object(robot.rt, "prepare_optix_rays_2d", return_value=_FakePreparedRays()),
        ):
            payload = robot.run_app("optix", optix_summary_mode="prepared_count")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_prepared_any_hit_count")
        self.assertEqual(payload["output_mode"], "hit_count")
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

    def test_row_mode_compact_outputs_do_not_overstate_native_continuation(self) -> None:
        for output_mode in ("full", "pose_flags", "hit_count"):
            with self.subTest(output_mode=output_mode):
                payload = robot.run_app("cpu_python_reference", output_mode=output_mode)
                self.assertFalse(payload["native_continuation_active"])
                self.assertEqual(payload["native_continuation_backend"], "none")
                self.assertTrue(payload["matches_oracle"])


if __name__ == "__main__":
    unittest.main()
