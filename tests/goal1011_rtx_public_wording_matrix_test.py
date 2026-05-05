from __future__ import annotations

import unittest

import rtdsl as rt


REVIEWED_APPS = {
    "service_coverage_gaps",
    "event_hotspot_screening",
    "outlier_detection",
    "dbscan_clustering",
    "robot_collision_screening",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "ann_candidate_search",
    "facility_knn_assignment",
    "road_hazard_screening",
    "hausdorff_distance",
    "barnes_hut_force_app",
    "polygon_pair_overlap_area_rows",
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
        self.assertEqual(len(reviewed), 13)

    def test_reviewed_rows_are_bounded_to_named_subpaths(self) -> None:
        matrix = rt.rtx_public_wording_matrix()
        for app in REVIEWED_APPS:
            row = matrix[app]
            if app in {"facility_knn_assignment", "barnes_hut_force_app"}:
                self.assertEqual(row.evidence, "Goal1146")
            elif app == "road_hazard_screening":
                self.assertEqual(row.evidence, "Goal1208")
            elif app == "hausdorff_distance":
                self.assertEqual(row.evidence, "Goal1224")
            elif app == "polygon_pair_overlap_area_rows":
                self.assertEqual(row.evidence, "Goal1263")
            elif app == "robot_collision_screening":
                self.assertEqual(row.evidence, "Goal1126")
            elif app == "event_hotspot_screening":
                self.assertEqual(row.evidence, "Goal1061")
            else:
                self.assertIn("Goal1008/Goal1009", row.evidence)
            self.assertIn("sub-path", row.reviewed_wording)
            self.assertTrue(
                "same-semantics baseline" in row.reviewed_wording
                or "same-contract" in row.reviewed_wording
                or "per-pose throughput" in row.reviewed_wording
                or "same-scale Embree sub-path" in row.reviewed_wording
                or "same-contract Embree" in row.reviewed_wording
            )
            self.assertNotIn("whole app", row.reviewed_wording.lower())
            self.assertNotIn("default mode", row.reviewed_wording.lower())
            self.assertNotIn("python-postprocess", row.reviewed_wording.lower())
            self.assertNotIn("broad rt-core", row.reviewed_wording.lower())

    def test_robot_keeps_rt_core_ready_with_normalized_public_wording(self) -> None:
        readiness = rt.optix_app_benchmark_readiness("robot_collision_screening")
        maturity = rt.rt_core_app_maturity("robot_collision_screening")
        wording = rt.rtx_public_wording_status("robot_collision_screening")

        self.assertEqual(readiness.status, "ready_for_rtx_claim_review")
        self.assertEqual(maturity.current_status, "rt_core_ready")
        self.assertEqual(wording.status, "public_wording_reviewed")
        self.assertEqual(wording.evidence, "Goal1126")
        self.assertIn("normalized per-pose", wording.boundary)
        self.assertIn("whole-app planning speedup", wording.boundary)
        self.assertIn("918.91x", wording.reviewed_wording)

    def test_goal1146_superseded_rows_are_promoted_after_review(self) -> None:
        wording = rt.rtx_public_wording_status("facility_knn_assignment")
        barnes = rt.rtx_public_wording_status("barnes_hut_force_app")

        self.assertEqual(wording.status, "public_wording_reviewed")
        self.assertEqual(wording.evidence, "Goal1146")
        self.assertIn("0.111619", wording.reviewed_wording)
        self.assertIn("80.60x", wording.reviewed_wording)
        self.assertIn("whole-app speedup", wording.boundary)
        self.assertEqual(barnes.status, "public_wording_reviewed")
        self.assertEqual(barnes.evidence, "Goal1146")
        self.assertIn("0.222256", barnes.reviewed_wording)
        self.assertIn("240.56x", barnes.reviewed_wording)
        self.assertIn("force-vector reduction", barnes.boundary)

    def test_goal1208_promotes_only_bounded_road_hazard_wording(self) -> None:
        wording = rt.rtx_public_wording_status("road_hazard_screening")
        self.assertEqual(wording.status, "public_wording_reviewed")
        self.assertEqual(wording.evidence, "Goal1208")
        self.assertIn("0.230652", wording.reviewed_wording)
        self.assertIn("3.53x", wording.reviewed_wording)
        self.assertIn("40k copies", wording.reviewed_wording)
        self.assertIn("prepared native road-hazard compact-summary", wording.boundary)
        self.assertIn("full GIS/routing", wording.boundary)
        self.assertIn("whole-app road-hazard speedup", wording.boundary)

    def test_goal1224_and_goal1263_resolve_remaining_not_reviewed_rows(self) -> None:
        graph = rt.rtx_public_wording_status("graph_analytics")
        polygon_pair = rt.rtx_public_wording_status("polygon_pair_overlap_area_rows")
        hausdorff = rt.rtx_public_wording_status("hausdorff_distance")

        self.assertEqual(graph.status, "public_wording_blocked")
        self.assertEqual(graph.evidence, "Goal1224/Goal1264")
        self.assertIn("total OptiX path slower than Embree", graph.reviewed_wording)
        self.assertIn("host-side input construction", graph.reviewed_wording)
        self.assertIn("BFS frontier bookkeeping", graph.boundary)
        self.assertEqual(polygon_pair.status, "public_wording_reviewed")
        self.assertEqual(polygon_pair.evidence, "Goal1263")
        self.assertIn("1.4x", polygon_pair.reviewed_wording)
        self.assertIn("1.2x", polygon_pair.reviewed_wording)
        self.assertIn("exact polygon-area continuation", polygon_pair.boundary)
        self.assertEqual(hausdorff.status, "public_wording_reviewed")
        self.assertEqual(hausdorff.evidence, "Goal1224")
        self.assertIn("0.122389", hausdorff.reviewed_wording)
        self.assertIn("13.73x", hausdorff.reviewed_wording)
        self.assertIn("exact Hausdorff distance", hausdorff.boundary)

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
