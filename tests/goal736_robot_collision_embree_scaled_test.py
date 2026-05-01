import unittest

from examples import rtdl_robot_collision_screening_app as app


class Goal736RobotCollisionEmbreeScaledTest(unittest.TestCase):
    def test_scaled_hit_count_matches_cpu_reference(self) -> None:
        expected = app.run_app(
            "cpu_python_reference",
            output_mode="hit_count",
            pose_count=64,
            obstacle_count=16,
        )
        actual = app.run_app(
            "embree",
            output_mode="hit_count",
            pose_count=64,
            obstacle_count=16,
        )

        self.assertEqual(actual["pose_count"], 64)
        self.assertEqual(actual["edge_ray_count"], 256)
        self.assertEqual(actual["obstacle_triangle_count"], 32)
        self.assertEqual(actual["hit_edge_count"], expected["hit_edge_count"])
        self.assertTrue(actual["matches_oracle"])

    def test_scaled_pose_flags_omits_witness_rows(self) -> None:
        payload = app.run_app(
            "cpu_python_reference",
            output_mode="pose_flags",
            pose_count=32,
            obstacle_count=9,
        )

        self.assertEqual(payload["output_mode"], "pose_flags")
        self.assertEqual(payload["pose_count"], 32)
        self.assertEqual(len(payload["pose_collision_flags"]), 32)
        self.assertNotIn("rows", payload)
        self.assertNotIn("edge_any_hit_rows", payload)

    def test_requires_pose_and_obstacle_counts_together(self) -> None:
        with self.assertRaisesRegex(ValueError, "provided together"):
            app.run_app("cpu_python_reference", output_mode="hit_count", pose_count=4)
        with self.assertRaisesRegex(ValueError, "provided together"):
            app.run_app("cpu_python_reference", output_mode="hit_count", obstacle_count=4)

    def test_rejects_invalid_scaled_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "pose_count must be positive"):
            app.make_scaled_case(pose_count=0, obstacle_count=1)
        with self.assertRaisesRegex(ValueError, "obstacle_count must be positive"):
            app.make_scaled_case(pose_count=1, obstacle_count=0)
        with self.assertRaisesRegex(ValueError, "pose_id_start must be positive"):
            app.make_scaled_case(pose_count=1, obstacle_count=1, pose_id_start=0)

    def test_scaled_case_can_start_at_later_pose_id_for_chunked_baselines(self) -> None:
        case = app.make_scaled_case(pose_count=3, obstacle_count=4, pose_id_start=200001)
        pose_ids = [int(pose["pose_id"]) for pose in case["poses"]]

        self.assertEqual(pose_ids, [200001, 200002, 200003])
        self.assertEqual(case["edge_rays"][0].id // 1000, 200001)

    def test_scaled_case_can_use_compact_ray_ids_for_native_chunks(self) -> None:
        case = app.make_scaled_case(
            pose_count=3,
            obstacle_count=4,
            pose_id_start=200001,
            compact_ray_ids=True,
        )
        ray_ids = [int(ray.id) for ray in case["edge_rays"][:5]]

        self.assertEqual(ray_ids, [0, 1, 2, 3, 4])
        self.assertEqual(case["ray_metadata"][0]["pose_id"], 200001)
        self.assertEqual(case["ray_metadata"][4]["pose_id"], 200002)


if __name__ == "__main__":
    unittest.main()
