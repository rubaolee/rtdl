import json
import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt
from scripts.goal1659_v1_6_11_perf_matrix import (
    VERSION,
    build_manifest,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1659_v1_6_11_perf_matrix.py"
REPORT = ROOT / "docs" / "reports" / "goal1659_v1_6_11_perf_matrix_2026-05-10.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal1659_v1_6_11_perf_matrix_2026-05-10.json"
PREFLIGHT = ROOT / "docs" / "reports" / "goal1659_v1_6_11_local_command_preflight_2026-05-10.md"
PREFLIGHT_JSON = ROOT / "docs" / "reports" / "goal1659_v1_6_11_local_command_preflight_2026-05-10.json"


class Goal1659V1611PerfMatrixTest(unittest.TestCase):
    def test_manifest_covers_every_public_app(self) -> None:
        payload = validate_manifest(build_manifest())
        self.assertEqual(payload["version"], "v1.6.11")
        self.assertEqual(set(payload["covered_apps"]), set(rt.public_apps()))
        self.assertEqual(payload["entry_count"], len(rt.public_apps()))

    def test_manifest_is_release_fail_closed_until_evidence(self) -> None:
        payload = validate_manifest(build_manifest())
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["tag_authorized"])
        self.assertFalse(payload["pod_needed_now"])
        self.assertTrue(payload["pod_required_for_final_perf_evidence"])
        for claim in [
            "whole_app_speedup",
            "broad_rtx_or_gpu_acceleration",
            "true_zero_copy",
            "stable_collect_k_bounded_promotion",
            "python_partner_rtdl",
        ]:
            with self.subTest(claim=claim):
                self.assertIn(claim, payload["blocked_claims"])
        criteria = payload["pod_pass_criteria"]
        self.assertEqual(criteria["active_pod_rows"], 16)
        self.assertEqual(criteria["minimum_completed_rows_for_release_candidate"], 16)
        self.assertIn("robot_collision_screening", criteria["required_positive_control_apps"])
        self.assertIn("All 16 active pod rows", criteria["release_candidate_pass_rule"])
        self.assertIn("authorizes no positive wording", criteria["public_speedup_wording_rule"])

    def test_every_entry_has_baseline_acceptance_and_no_claim(self) -> None:
        payload = validate_manifest(build_manifest())
        pod_entries = 0
        for entry in payload["entries"]:
            with self.subTest(app=entry["app"]):
                self.assertTrue(entry["scope"])
                self.assertTrue(entry["baseline"])
                self.assertTrue(entry["acceptance"])
                self.assertFalse(entry["public_claim_allowed_from_this_manifest_alone"])
                if entry["pod_command"]:
                    pod_entries += 1
        self.assertGreaterEqual(pod_entries, 12)

    def test_key_apps_have_expected_perf_scope(self) -> None:
        payload = validate_manifest(build_manifest())
        by_app = {entry["app"]: entry for entry in payload["entries"]}
        self.assertIn("compact-summary DB", by_app["database_analytics"]["scope"])
        self.assertIn("prepared ray/triangle any-hit", by_app["robot_collision_screening"]["scope"])
        self.assertIn("bounded candidate", by_app["polygon_set_jaccard"]["scope"])
        self.assertIn("shares the Goal757 fixed-radius prepared fixture", by_app["outlier_detection"]["notes"])
        self.assertIn("shares the Goal757 fixed-radius prepared fixture", by_app["dbscan_clustering"]["notes"])
        self.assertIn("`--skip-validation` is used", by_app["facility_knn_assignment"]["notes"])
        self.assertIn("`--skip-validation` is used", by_app["robot_collision_screening"]["notes"])
        self.assertIsNone(by_app["apple_rt_demo"]["pod_command"])
        self.assertIsNone(by_app["hiprt_ray_triangle_hitcount"]["pod_command"])

    def test_cli_writes_reports(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--json-out",
                str(JSON_REPORT),
                "--md-out",
                str(REPORT),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["version"], VERSION)
        self.assertTrue(JSON_REPORT.exists())
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1.6.11", text)
        self.assertIn("Pod required for final NVIDIA OptiX performance evidence", text)
        self.assertIn("does not publish the release or authorize a tag", text)
        self.assertIn("All 16 active pod rows", text)
        self.assertIn("authorizes no positive wording", text)

    def test_local_preflight_artifact_is_green(self) -> None:
        self.assertTrue(PREFLIGHT.exists())
        self.assertTrue(PREFLIGHT_JSON.exists())
        payload = json.loads(PREFLIGHT_JSON.read_text(encoding="utf-8"))
        self.assertTrue(payload["accepted"])
        rows = payload["rows"]
        self.assertEqual(len(rows), len(rt.public_apps()))
        self.assertEqual(sum(row["status"] == "fail" for row in rows), 0)
        text = PREFLIGHT.read_text(encoding="utf-8")
        self.assertIn("accepted_local_preflight", text)
        self.assertIn("No pod is needed for this local preflight", text)
        self.assertIn("pod is still required for final", text)


if __name__ == "__main__":
    unittest.main()
