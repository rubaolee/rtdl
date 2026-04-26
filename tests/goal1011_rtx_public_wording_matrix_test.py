from __future__ import annotations

import unittest

import rtdsl as rt


REVIEWED_APPS = {
    "service_coverage_gaps",
    "outlier_detection",
    "dbscan_clustering",
    "facility_knn_assignment",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "ann_candidate_search",
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
        self.assertEqual(len(reviewed), 7)

    def test_reviewed_rows_are_bounded_to_named_subpaths(self) -> None:
        matrix = rt.rtx_public_wording_matrix()
        for app in REVIEWED_APPS:
            row = matrix[app]
            self.assertIn("Goal1008/Goal1009", row.evidence)
            self.assertIn("sub-path", row.reviewed_wording)
            self.assertIn("same-semantics baseline", row.reviewed_wording)
            self.assertNotIn("whole app", row.reviewed_wording.lower())
            self.assertNotIn("default mode", row.reviewed_wording.lower())
            self.assertNotIn("python-postprocess", row.reviewed_wording.lower())
            self.assertNotIn("broad rt-core", row.reviewed_wording.lower())

    def test_robot_keeps_rt_core_ready_but_blocks_public_speedup_wording(self) -> None:
        readiness = rt.optix_app_benchmark_readiness("robot_collision_screening")
        maturity = rt.rt_core_app_maturity("robot_collision_screening")
        wording = rt.rtx_public_wording_status("robot_collision_screening")

        self.assertEqual(readiness.status, "ready_for_rtx_claim_review")
        self.assertEqual(maturity.current_status, "rt_core_ready")
        self.assertEqual(wording.status, "public_wording_blocked")
        self.assertEqual(wording.evidence, "Goal1008")
        self.assertIn("real RT-core path", wording.boundary)
        self.assertIn("100 ms", wording.boundary)

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
