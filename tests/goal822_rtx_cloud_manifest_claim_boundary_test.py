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
            "facility_knn_assignment",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
            "hausdorff_distance",
            "ann_candidate_search",
            "barnes_hut_force_app",
        ):
            with self.subTest(app=app):
                self.assertNotIn(app, active_apps)
                self.assertIn(app, manifest["excluded_apps"])

    def test_spatial_apps_waiting_on_real_rtx_artifacts_are_deferred_not_active(self) -> None:
        manifest = build_manifest()
        active_apps = {entry["app"] for entry in manifest["entries"]}
        deferred = {entry["app"]: entry for entry in manifest["deferred_entries"]}
        for app in ("service_coverage_gaps", "event_hotspot_screening"):
            with self.subTest(app=app):
                self.assertNotIn(app, active_apps)
                self.assertIn(app, deferred)
                self.assertEqual(deferred[app]["benchmark_readiness"], "needs_real_rtx_artifact")
                self.assertIn("Goal811", deferred[app]["activation_gate"])


if __name__ == "__main__":
    unittest.main()
