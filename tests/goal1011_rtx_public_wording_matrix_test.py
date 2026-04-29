from __future__ import annotations

import unittest

import rtdsl as rt


REVIEWED_APPS = {
    "service_coverage_gaps",
    "event_hotspot_screening",
    "outlier_detection",
    "dbscan_clustering",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "ann_candidate_search",
    "facility_knn_assignment",
    "robot_collision_screening",
    "barnes_hut_force_app",
}


class Goal1011RtxPublicWordingMatrixTest(unittest.TestCase):
    def test_every_public_app_has_public_wording_row(self) -> None:
        matrix = rt.rtx_public_wording_matrix()
        self.assertEqual(set(matrix), set(rt.public_apps()))
        for app, row in matrix.items():
            self.assertEqual(row.app, app)
            self.assertIn(row.status, rt.RTX_PUBLIC_WORDING_STATUSES)

    def test_goal1009_reviewed_public_wording_set_is_exact(self) -> None:
        matrix = rt.rtx_public_wording_matrix()
        reviewed = {
            app
            for app, row in matrix.items()
            if row.status == "public_wording_reviewed"
        }
        self.assertEqual(reviewed, REVIEWED_APPS)
        self.assertEqual(len(reviewed), 10)

    def test_reviewed_rows_are_bounded_to_named_subpaths(self) -> None:
        matrix = rt.rtx_public_wording_matrix()
        for app in REVIEWED_APPS:
            row = matrix[app]
            if app == "event_hotspot_screening":
                self.assertEqual(row.evidence, "Goal1061")
            elif app in {"facility_knn_assignment", "barnes_hut_force_app"}:
                self.assertIn("Goal1121/Goal1123", row.evidence)
            elif app == "robot_collision_screening":
                self.assertIn("Goal1126", row.evidence)
            else:
                self.assertIn("Goal1008/Goal1009", row.evidence)
            self.assertIn("sub-path", row.reviewed_wording)
            self.assertTrue(
                "same-semantics baseline" in row.reviewed_wording
                or "same-contract" in row.reviewed_wording
                or "per-pose throughput" in row.reviewed_wording
            )
            self.assertNotIn("whole app", row.reviewed_wording.lower())
            self.assertNotIn("default mode", row.reviewed_wording.lower())
            self.assertNotIn("python-postprocess", row.reviewed_wording.lower())
            self.assertNotIn("broad rt-core", row.reviewed_wording.lower())

    def test_robot_keeps_rt_core_ready_and_has_normalized_public_wording(self) -> None:
        readiness = rt.optix_app_benchmark_readiness("robot_collision_screening")
        maturity = rt.rt_core_app_maturity("robot_collision_screening")
        wording = rt.rtx_public_wording_status("robot_collision_screening")

        self.assertEqual(readiness.status, "ready_for_rtx_claim_review")
        self.assertEqual(maturity.current_status, "rt_core_ready")
        self.assertEqual(wording.status, "public_wording_reviewed")
        self.assertEqual(wording.evidence, "Goal1121/Goal1123/Goal1126")
        self.assertIn("917.75x per-pose", wording.reviewed_wording)
        self.assertIn("normalized per-pose", wording.boundary)
        self.assertIn("not a same-total-work wall-time claim", wording.boundary)

    def test_facility_and_barnes_hut_have_goal1123_reviewed_wording(self) -> None:
        wording = rt.rtx_public_wording_status("facility_knn_assignment")
        barnes = rt.rtx_public_wording_status("barnes_hut_force_app")

        self.assertEqual(wording.status, "public_wording_reviewed")
        self.assertEqual(wording.evidence, "Goal1121/Goal1123")
        self.assertIn("coverage-threshold RTX query sub-path", wording.reviewed_wording)
        self.assertIn("whole-app speedup", wording.boundary)
        self.assertEqual(barnes.status, "public_wording_reviewed")
        self.assertEqual(barnes.evidence, "Goal1121/Goal1123")
        self.assertIn("Barnes-Hut node-coverage RTX query sub-path", barnes.reviewed_wording)
        self.assertIn("force-vector reduction", barnes.boundary)

    def test_non_nvidia_apps_are_excluded_from_public_rtx_wording(self) -> None:
        for app in ("apple_rt_demo", "hiprt_ray_triangle_hitcount"):
            row = rt.rtx_public_wording_status(app)
            self.assertEqual(row.status, "not_nvidia_public_wording_target")
            self.assertIn("outside NVIDIA RTX", row.reviewed_wording)

    def test_unknown_app_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown RTDL app"):
            rt.rtx_public_wording_status("missing_app")


if __name__ == "__main__":
    unittest.main()
