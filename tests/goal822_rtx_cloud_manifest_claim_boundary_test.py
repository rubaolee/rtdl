import unittest

import rtdsl as rt
from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest


class Goal822RtxCloudManifestClaimBoundaryTest(unittest.TestCase):
    def test_active_entries_are_only_ready_or_partial_rt_core_paths(self) -> None:
        manifest = build_manifest()
        for entry in manifest["entries"]:
            with self.subTest(app=entry["app"], path_name=entry["path_name"]):
                maturity = rt.rt_core_app_maturity(entry["app"])
                self.assertIn(maturity.current_status, {"rt_core_ready", "rt_core_partial_ready"})
                self.assertNotIn(entry["benchmark_readiness"], {"exclude_from_rtx_app_benchmark", "needs_native_kernel_tuning"})
                self.assertNotIn(entry["optix_performance_class"], {"cuda_through_optix", "host_indexed_fallback", "not_optix_exposed"})

    def test_known_non_claim_apps_are_excluded_from_active_cloud_entries(self) -> None:
        manifest = build_manifest()
        active_apps = {entry["app"] for entry in manifest["entries"]}
        for app in (
            "graph_analytics",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            with self.subTest(app=app):
                self.assertNotIn(app, active_apps)
                self.assertIn(app, manifest["excluded_apps"])

    def test_deferred_regression_entries_are_ready_but_not_active(self) -> None:
        manifest = build_manifest()
        active_apps = {entry["app"] for entry in manifest["entries"]}
        deferred = {entry["app"]: entry for entry in manifest["deferred_entries"]}
        for app in (
            "graph_analytics",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "hausdorff_distance",
            "ann_candidate_search",
            "barnes_hut_force_app",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            with self.subTest(app=app):
                self.assertNotIn(app, active_apps)
                self.assertIn(app, deferred)
                self.assertEqual(deferred[app]["benchmark_readiness"], "ready_for_rtx_claim_review")
                self.assertTrue(deferred[app]["activation_gate"].strip())

    def test_reviewed_prepared_summaries_have_rtx_artifacts_and_are_active(self) -> None:
        manifest = build_manifest()
        active = {entry["app"]: entry for entry in manifest["entries"]}
        deferred_apps = {entry["app"] for entry in manifest["deferred_entries"]}
        for app in ("service_coverage_gaps", "event_hotspot_screening", "facility_knn_assignment"):
            with self.subTest(app=app):
                self.assertIn(app, active)
                self.assertNotIn(app, deferred_apps)
                self.assertEqual(active[app]["benchmark_readiness"], "ready_for_rtx_claim_review")
                if app == "facility_knn_assignment":
                    self.assertIn("Goal887/Goal920", active[app]["readiness_next_goal"])
                else:
                    self.assertIn("Goal917", active[app]["readiness_next_goal"])


if __name__ == "__main__":
    unittest.main()
