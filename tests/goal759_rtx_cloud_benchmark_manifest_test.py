import json
import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal759_rtx_cloud_benchmark_manifest.py"


class Goal759RtxCloudBenchmarkManifestTest(unittest.TestCase):
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

    def test_prepared_summary_apps_are_classified_without_whole_app_claims(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        by_app = {entry["app"]: entry for entry in payload["entries"]}

        self.assertEqual(by_app["outlier_detection"]["optix_performance_class"], "optix_traversal_prepared_summary")
        self.assertIn("prepared fixed-radius threshold summary", by_app["outlier_detection"]["claim_scope"])
        self.assertIn("whole-app RTX speedup", by_app["outlier_detection"]["non_claim"])

        self.assertEqual(by_app["dbscan_clustering"]["optix_performance_class"], "optix_traversal_prepared_summary")
        self.assertIn("prepared fixed-radius core-flag", by_app["dbscan_clustering"]["claim_scope"])
        self.assertIn("not a full DBSCAN", by_app["dbscan_clustering"]["non_claim"])

    def test_excluded_cuda_through_optix_apps_do_not_enter_manifest_entries(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        manifest_apps = {entry["app"] for entry in payload["entries"]}
        excluded = {"hausdorff_distance", "ann_candidate_search", "barnes_hut_force_app"}
        self.assertTrue(excluded.isdisjoint(manifest_apps))
        self.assertTrue(excluded.issubset(payload["excluded_apps"]))

    def test_robot_entry_uses_current_prepared_pose_flag_status(self):
        payload = __import__(
            "scripts.goal759_rtx_cloud_benchmark_manifest",
            fromlist=["build_manifest"],
        ).build_manifest()
        robot = next(entry for entry in payload["entries"] if entry["app"] == "robot_collision_screening")
        self.assertEqual(robot["optix_performance_class"], "optix_traversal")
        self.assertIn("prepared_pose_flags", robot["command"])
        self.assertIn("prepared native pose-flag summary", robot["optix_performance_note"])
        self.assertNotIn("future ABI work", robot["optix_performance_note"])

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
