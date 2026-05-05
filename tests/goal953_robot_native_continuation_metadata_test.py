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


class _FakeGenericGroupedPoseFlags:
    def __init__(self, pose_flags=(False, True, True, False)):
        self.pose_flags = tuple(pose_flags)

    def __call__(
        self,
        *,
        triangles,
        rays,
        group_indices,
        group_count: int,
        backend: str,
        threshold: int = 1,
        query_repeats: int = 1,
        prepare_scene=None,
        prepare_rays=None,
        prepare_group_indices=None,
    ):
        group_flags = self.pose_flags[:group_count]
        return {
            "primitive": "ANY_HIT",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "result_layout": "grouped_threshold_bool",
            "group_flags": group_flags,
            "threshold_reached_count": sum(1 for flag in group_flags if flag),
            "run_phases": {
                "scene_prepare_sec": 0.001,
                "ray_prepare_sec": 0.001,
                "group_index_prepare_sec": 0.001,
                "query_grouped_count_threshold_bool_sec": 0.001,
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
        with mock.patch.object(
            robot.rt,
            "run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool",
            side_effect=_FakeGenericGroupedPoseFlags(pose_flags=(False, True, True, False)),
        ):
            payload = robot.run_app("optix", optix_summary_mode="prepared_pose_flags")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_prepared_pose_flags")
        self.assertEqual(payload["output_mode"], "pose_flags")
        self.assertEqual(payload["prepared_summary"]["generic_primitive"], "ANY_HIT")
        self.assertEqual(payload["prepared_summary"]["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(payload["prepared_summary"]["result_layout"], "grouped_threshold_bool")
        self.assertTrue(payload["matches_oracle"])

    def test_prepared_pose_flags_scaled_fixture_uses_cpu_validation(self) -> None:
        oracle_rows = (
            {"ray_id": 1010, "any_hit": False},
            {"ray_id": 1011, "any_hit": False},
            {"ray_id": 1012, "any_hit": False},
            {"ray_id": 1013, "any_hit": False},
            {"ray_id": 2010, "any_hit": True},
            {"ray_id": 2011, "any_hit": False},
            {"ray_id": 2012, "any_hit": False},
            {"ray_id": 2013, "any_hit": False},
            {"ray_id": 3010, "any_hit": False},
            {"ray_id": 3011, "any_hit": False},
            {"ray_id": 3012, "any_hit": False},
            {"ray_id": 3013, "any_hit": False},
            {"ray_id": 4010, "any_hit": True},
            {"ray_id": 4011, "any_hit": False},
            {"ray_id": 4012, "any_hit": False},
            {"ray_id": 4013, "any_hit": False},
        )
        with (
            mock.patch(
                "examples.rtdl_robot_collision_screening_app.rt.ray_triangle_any_hit_cpu",
                return_value=oracle_rows,
            ),
            mock.patch.object(
                robot.rt,
                "run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool",
                side_effect=_FakeGenericGroupedPoseFlags(pose_flags=(False, True, False, True)),
            ),
        ):
            payload = robot.run_app(
                "optix",
                optix_summary_mode="prepared_pose_flags",
                pose_count=4,
                obstacle_count=4,
            )

        self.assertEqual(payload["validation_mode"], "cpu_oracle")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["oracle_colliding_pose_ids"], [2, 4])

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
