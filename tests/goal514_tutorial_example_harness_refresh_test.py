from __future__ import annotations

import unittest

from scripts.goal410_tutorial_example_check import public_cases, should_skip


class Goal514TutorialExampleHarnessRefreshTest(unittest.TestCase):
    def test_v0_8_linux_backend_cases_match_public_docs(self) -> None:
        cases = {str(case["name"]): case for case in public_cases()}

        self.assertEqual(
            cases["hausdorff_distance_app_optix"]["args"],
            ["examples/rtdl_hausdorff_distance_app.py", "--backend", "optix"],
        )
        self.assertEqual(
            cases["hausdorff_distance_app_vulkan"]["args"],
            ["examples/rtdl_hausdorff_distance_app.py", "--backend", "vulkan"],
        )
        self.assertEqual(
            cases["ann_candidate_app_optix"]["args"],
            ["examples/rtdl_ann_candidate_app.py", "--backend", "optix"],
        )
        self.assertEqual(
            cases["ann_candidate_app_vulkan"]["args"],
            ["examples/rtdl_ann_candidate_app.py", "--backend", "vulkan"],
        )
        self.assertEqual(
            cases["outlier_detection_app_optix"]["args"],
            ["examples/rtdl_outlier_detection_app.py", "--backend", "optix"],
        )
        self.assertEqual(
            cases["outlier_detection_app_vulkan"]["args"],
            ["examples/rtdl_outlier_detection_app.py", "--backend", "vulkan"],
        )
        self.assertEqual(
            cases["dbscan_clustering_app_optix"]["args"],
            ["examples/rtdl_dbscan_clustering_app.py", "--backend", "optix"],
        )
        self.assertEqual(
            cases["dbscan_clustering_app_vulkan"]["args"],
            ["examples/rtdl_dbscan_clustering_app.py", "--backend", "vulkan"],
        )
        self.assertEqual(
            cases["robot_collision_screening_app_optix"]["args"],
            ["examples/rtdl_robot_collision_screening_app.py", "--backend", "optix"],
        )
        self.assertEqual(
            cases["barnes_hut_force_app_optix"]["args"],
            ["examples/rtdl_barnes_hut_force_app.py", "--backend", "optix"],
        )
        self.assertEqual(
            cases["barnes_hut_force_app_vulkan"]["args"],
            ["examples/rtdl_barnes_hut_force_app.py", "--backend", "vulkan"],
        )

        for name in (
            "hausdorff_distance_app_optix",
            "hausdorff_distance_app_vulkan",
            "ann_candidate_app_optix",
            "ann_candidate_app_vulkan",
            "outlier_detection_app_optix",
            "outlier_detection_app_vulkan",
            "dbscan_clustering_app_optix",
            "dbscan_clustering_app_vulkan",
            "robot_collision_screening_app_optix",
            "barnes_hut_force_app_optix",
            "barnes_hut_force_app_vulkan",
        ):
            self.assertTrue(cases[name]["linux_only"])

    def test_optional_video_dependency_has_explicit_skip_reason(self) -> None:
        cases = {str(case["name"]): case for case in public_cases()}
        render_case = cases["render_hidden_star_chunked_video"]

        self.assertEqual(render_case["python_modules"], ("imageio", "imageio_ffmpeg"))
        synthetic_missing = {
            **render_case,
            "python_modules": ("__rtdl_missing_goal514_dependency__",),
        }
        self.assertEqual(
            should_skip(synthetic_missing, {"cpu_python_reference": True}, "Linux"),
            "missing_python_module___rtdl_missing_goal514_dependency__",
        )


if __name__ == "__main__":
    unittest.main()
