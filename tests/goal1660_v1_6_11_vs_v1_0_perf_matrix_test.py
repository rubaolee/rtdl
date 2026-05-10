import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from scripts.goal1660_v1_6_11_vs_v1_0_perf_matrix import (
    BASELINE_VERSION,
    CURRENT_VERSION,
    build_manifest,
    validate_manifest,
)


SCRIPT = ROOT / "scripts" / "goal1660_v1_6_11_vs_v1_0_perf_matrix.py"
REPORT = ROOT / "docs" / "reports" / "goal1660_v1_6_11_vs_v1_0_perf_matrix_2026-05-10.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal1660_v1_6_11_vs_v1_0_perf_matrix_2026-05-10.json"


class Goal1660V1611VsV10PerfMatrixTest(unittest.TestCase):
    def test_manifest_has_one_embree_and_one_optix_row_per_public_app(self) -> None:
        payload = validate_manifest(build_manifest())
        self.assertEqual(payload["current_version"], CURRENT_VERSION)
        self.assertEqual(payload["baseline_version"], BASELINE_VERSION)
        self.assertEqual(payload["row_count"], len(rt.public_apps()) * 2)
        pairs = {(row["app"], row["engine"]) for row in payload["rows"]}
        for app in rt.public_apps():
            self.assertIn((app, "embree"), pairs)
            self.assertIn((app, "optix"), pairs)

    def test_manifest_is_fail_closed_and_pod_required(self) -> None:
        payload = validate_manifest(build_manifest())
        self.assertTrue(payload["requires_pod"])
        self.assertTrue(payload["pod_needed_after_local_preflight"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["tag_authorized"])
        self.assertFalse(payload["public_claim_authorized"])
        for claim in [
            "whole_app_speedup",
            "broad_rtx_or_gpu_acceleration",
            "true_zero_copy",
            "stable_collect_k_bounded_promotion",
            "python_partner_rtdl",
            "v1_6_11_release_tag_action",
        ]:
            self.assertIn(claim, payload["blocked_claims"])

    def test_frozen_or_non_applicable_apps_are_excluded_not_faked(self) -> None:
        payload = validate_manifest(build_manifest())
        by_pair = {(row["app"], row["engine"]): row for row in payload["rows"]}
        self.assertEqual(by_pair[("apple_rt_demo", "embree")]["status"], "excluded")
        self.assertEqual(by_pair[("apple_rt_demo", "optix")]["status"], "excluded")
        self.assertEqual(by_pair[("hiprt_ray_triangle_hitcount", "embree")]["status"], "excluded")
        self.assertEqual(by_pair[("hiprt_ray_triangle_hitcount", "optix")]["status"], "excluded")
        self.assertEqual(by_pair[("graph_analytics", "embree")]["status"], "excluded")
        self.assertEqual(by_pair[("graph_analytics", "optix")]["status"], "planned")
        self.assertEqual(by_pair[("outlier_detection", "embree")]["status"], "excluded")
        self.assertEqual(by_pair[("outlier_detection", "optix")]["status"], "planned")
        self.assertEqual(by_pair[("dbscan_clustering", "embree")]["status"], "excluded")
        self.assertEqual(by_pair[("dbscan_clustering", "optix")]["status"], "shared_primitive_alias")
        self.assertEqual(
            by_pair[("dbscan_clustering", "optix")]["shared_primitive_canonical"],
            "outlier_detection",
        )
        self.assertFalse(by_pair[("dbscan_clustering", "optix")]["compare_v1_0"])

    def test_key_apps_have_both_engine_commands_when_supported(self) -> None:
        payload = validate_manifest(build_manifest())
        by_pair = {(row["app"], row["engine"]): row for row in payload["rows"]}
        for app in ["database_analytics", "robot_collision_screening", "polygon_set_jaccard"]:
            for engine in ["embree", "optix"]:
                with self.subTest(app=app, engine=engine):
                    row = by_pair[(app, engine)]
                    self.assertEqual(row["status"], "planned")
                    self.assertIn(engine, row["v1_6_11_command"])
                    self.assertIn(engine, row["v1_0_command"])
                    self.assertTrue(row["script_exists_in_v1_0"])

    def test_no_engine_selector_rows_are_not_decorative_engine_claims(self) -> None:
        payload = validate_manifest(build_manifest())
        by_pair = {(row["app"], row["engine"]): row for row in payload["rows"]}
        graph_embree = by_pair[("graph_analytics", "embree")]
        self.assertEqual(graph_embree["engine_selector"], "none")
        self.assertIn("decorative engine label", graph_embree["reason"])
        graph_optix = by_pair[("graph_analytics", "optix")]
        self.assertEqual(graph_optix["engine_selector"], "optix_specific_script")

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
        self.assertEqual(summary["current"], CURRENT_VERSION)
        self.assertEqual(summary["baseline"], BASELINE_VERSION)
        self.assertTrue(JSON_REPORT.exists())
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1.6.11 vs v1.0", text)
        self.assertIn("one Embree row and one OptiX", text)
        self.assertIn("two clean checkouts", text)
        self.assertIn("does not authorize release or public speedup claims", text)


if __name__ == "__main__":
    unittest.main()
