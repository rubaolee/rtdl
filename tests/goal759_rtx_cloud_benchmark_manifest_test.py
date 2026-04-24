import json
import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal759_rtx_cloud_benchmark_manifest.py"


class Goal759RtxCloudBenchmarkManifestTest(unittest.TestCase):
    def test_goal832_two_ai_consensus_artifacts_exist(self):
        ledger = ROOT / "docs" / "reports" / "goal832_two_ai_consensus_2026-04-23.md"
        codex = ROOT / "docs" / "reports" / "goal832_codex_consensus_review_2026-04-23.md"
        gemini = ROOT / "docs" / "reports" / "goal832_gemini_external_consensus_review_2026-04-23.md"

        for path in (ledger, codex, gemini):
            self.assertTrue(path.exists(), str(path))

        ledger_text = ledger.read_text(encoding="utf-8")
        self.assertIn("Codex: ACCEPT", ledger_text)
        self.assertIn("Gemini 2.5 Flash: ACCEPT", ledger_text)
        self.assertIn("No Claude verdict is claimed", ledger_text)

    def test_manifest_entries_match_machine_readable_matrices(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        apps = set(rt.public_apps())
        self.assertEqual(payload["goal"], "Goal759 RTX cloud benchmark manifest")
        self.assertIn("does not authorize RTX speedup claims", payload["boundary"])

        entries = payload["entries"]
        self.assertGreaterEqual(len(entries), 5)
        for entry in entries:
            with self.subTest(entry=entry["path_name"]):
                self.assertIn(entry["app"], apps)
                self.assertEqual(
                    entry["optix_performance_class"],
                    rt.optix_app_performance_support(entry["app"]).performance_class,
                )
                self.assertEqual(
                    entry["benchmark_readiness"],
                    rt.optix_app_benchmark_readiness(entry["app"]).status,
                )
                self.assertTrue(entry["command"])
                self.assertTrue(entry["claim_scope"])
                self.assertTrue(entry["non_claim"])
                self.assertTrue(entry["preconditions"])
                self.assertEqual(
                    entry["baseline_review_contract"]["status"],
                    "required_before_public_speedup_claim",
                )
                self.assertTrue(entry["baseline_review_contract"]["required_baselines"])
                self.assertTrue(entry["baseline_review_contract"]["requires_phase_separation"])

    def test_active_entries_have_comparable_baseline_contracts(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        by_path = {entry["path_name"]: entry for entry in payload["entries"]}

        db = by_path["prepared_db_session_sales_risk"]["baseline_review_contract"]
        self.assertIn("postgresql_same_semantics_on_linux_when_available", db["required_baselines"])
        self.assertIn("compact_summary prepared DB", db["comparable_metric_scope"])
        self.assertIn("not a DBMS", db["claim_limit"])

        fixed_radius = by_path["prepared_fixed_radius_density_summary"]["baseline_review_contract"]
        self.assertIn("cpu_scalar_threshold_count_oracle", fixed_radius["required_baselines"])
        self.assertIn("threshold-count", fixed_radius["claim_limit"])
        self.assertIn("full DBSCAN", fixed_radius["claim_limit"])

        robot = by_path["prepared_pose_flags"]["baseline_review_contract"]
        self.assertIn("embree_anyhit_pose_count_or_equivalent_compact_summary", robot["required_baselines"])
        self.assertIn("native_anyhit_query", robot["required_phases"])
        self.assertIn("not full robot planning", robot["claim_limit"])

    def test_prepared_summary_apps_are_classified_without_whole_app_claims(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        by_app = {entry["app"]: entry for entry in payload["entries"]}

        self.assertEqual(by_app["outlier_detection"]["optix_performance_class"], "optix_traversal_prepared_summary")
        self.assertIn("prepared fixed-radius threshold summary", by_app["outlier_detection"]["claim_scope"])
        self.assertIn("whole-app RTX speedup", by_app["outlier_detection"]["non_claim"])
        self.assertIn("--skip-validation", by_app["outlier_detection"]["command"])
        self.assertIn("--result-mode", by_app["outlier_detection"]["command"])
        self.assertIn("threshold_count", by_app["outlier_detection"]["command"])

        self.assertEqual(by_app["dbscan_clustering"]["optix_performance_class"], "optix_traversal_prepared_summary")
        self.assertIn("prepared fixed-radius core-flag", by_app["dbscan_clustering"]["claim_scope"])
        self.assertIn("not a full DBSCAN", by_app["dbscan_clustering"]["non_claim"])
        self.assertIn("--skip-validation", by_app["dbscan_clustering"]["command"])
        self.assertIn("--result-mode", by_app["dbscan_clustering"]["command"])
        self.assertIn("threshold_count", by_app["dbscan_clustering"]["command"])

    def test_prepared_decision_apps_are_deferred_not_active(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        manifest_apps = {entry["app"] for entry in payload["entries"]}
        deferred = {entry["app"] for entry in payload["deferred_entries"]}
        expected = {
            "hausdorff_distance",
            "ann_candidate_search",
            "facility_knn_assignment",
            "barnes_hut_force_app",
        }
        self.assertTrue(expected.isdisjoint(manifest_apps))
        self.assertTrue(expected.issubset(deferred))
        self.assertTrue(expected.isdisjoint(payload["excluded_apps"]))

    def test_robot_entry_uses_current_prepared_pose_flag_status(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        robot = next(entry for entry in payload["entries"] if entry["app"] == "robot_collision_screening")
        self.assertEqual(robot["optix_performance_class"], "optix_traversal")
        self.assertIn("scripts/goal760_optix_robot_pose_flags_phase_profiler.py", robot["command"])
        self.assertIn("--mode", robot["command"])
        self.assertIn("optix", robot["command"])
        self.assertIn("prepared native pose-flag summary", robot["optix_performance_note"])
        self.assertNotIn("future ABI work", robot["optix_performance_note"])

    def test_deferred_segment_polygon_entry_uses_goal807_gate(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        segment = next(
            entry
            for entry in payload["deferred_entries"]
            if entry["app"] == "segment_polygon_hitcount"
        )
        self.assertIn("scripts/goal807_segment_polygon_optix_mode_gate.py", segment["command"])
        self.assertIn("--strict", segment["command"])
        self.assertIn("Goal807 strict mode", segment["activation_gate"])
        self.assertEqual(segment["benchmark_readiness"], "needs_real_rtx_artifact")

    def test_deferred_road_hazard_entry_uses_goal888_gate(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        road = next(
            entry
            for entry in payload["deferred_entries"]
            if entry["app"] == "road_hazard_screening"
        )
        self.assertIn("scripts/goal888_road_hazard_native_optix_gate.py", road["command"])
        self.assertIn("--strict", road["command"])
        self.assertIn("--output-mode", road["command"])
        self.assertIn("summary", road["command"])
        self.assertEqual(road["benchmark_readiness"], "needs_real_rtx_artifact")
        self.assertIn("Goal888 strict mode", road["activation_gate"])

    def test_deferred_segment_polygon_anyhit_rows_entry_uses_goal873_gate(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        segment = next(
            entry
            for entry in payload["deferred_entries"]
            if entry["app"] == "segment_polygon_anyhit_rows"
        )
        self.assertIn("scripts/goal873_native_pair_row_optix_gate.py", segment["command"])
        self.assertIn("--strict", segment["command"])
        self.assertIn("--output-capacity", segment["command"])
        self.assertIn("Goal873 strict mode", segment["activation_gate"])
        self.assertIn("overflowed", segment["baseline_review_contract"]["required_phases"])
        self.assertIn("not default public app behavior", segment["non_claim"])

    def test_deferred_spatial_entries_use_goal811_profiler(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        deferred = {entry["app"]: entry for entry in payload["deferred_entries"]}
        for app in ("service_coverage_gaps", "event_hotspot_screening"):
            with self.subTest(app=app):
                self.assertIn("scripts/goal811_spatial_optix_summary_phase_profiler.py", deferred[app]["command"])
                self.assertIn("--mode", deferred[app]["command"])
                self.assertIn("optix", deferred[app]["command"])
                self.assertEqual(deferred[app]["benchmark_readiness"], "needs_real_rtx_artifact")
                self.assertIn("baseline_review_contract", deferred[app])
                self.assertIn("prepared compact summary", deferred[app]["baseline_review_contract"]["claim_limit"])

    def test_deferred_polygon_overlap_entries_use_goal877_profiler(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        deferred = {entry["app"]: entry for entry in payload["deferred_entries"]}
        for app in ("polygon_pair_overlap_area_rows", "polygon_set_jaccard"):
            with self.subTest(app=app):
                entry = deferred[app]
                self.assertIn("scripts/goal877_polygon_overlap_optix_phase_profiler.py", entry["command"])
                self.assertIn("--mode", entry["command"])
                self.assertIn("optix", entry["command"])
                self.assertIn("candidate discovery", entry["claim_scope"])
                self.assertIn("cpu_exact_refinement_sec", entry["baseline_review_contract"]["required_phases"])
                self.assertIn("not a full app RTX speedup claim", entry["non_claim"])

    def test_cli_emits_valid_json(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["goal"], "Goal759 RTX cloud benchmark manifest")
        self.assertGreaterEqual(len(payload["entries"]), 5)


if __name__ == "__main__":
    unittest.main()
