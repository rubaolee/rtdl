from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import rtdsl as rt
from scripts import goal947_v1_rtx_app_status_page as goal947


ROOT = Path(__file__).resolve().parents[1]


class Goal947V1RtxAppStatusPageTest(unittest.TestCase):
    def test_status_page_matches_live_matrices(self) -> None:
        payload = goal947.build_status_page()
        self.assertEqual(payload["summary"]["public_app_count"], len(rt.public_apps()))
        self.assertEqual(payload["summary"]["ready_for_rtx_claim_review"], 16)
        self.assertEqual(payload["summary"]["not_nvidia_rt_core_target"], 2)
        self.assertEqual(payload["summary"]["reviewed_public_wording"], 11)
        self.assertEqual(payload["summary"]["blocked_public_wording"], 0)
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["summary"]["broad_or_whole_app_public_speedup_claim_authorized"])
        self.assertEqual(
            payload["source_of_truth"]["public_wording"],
            "rtdsl.rtx_public_wording_matrix()",
        )

        rows = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), set(rt.public_apps()))
        for app, row in rows.items():
            with self.subTest(app=app):
                self.assertEqual(row["readiness_status"], rt.optix_app_benchmark_readiness(app).status)
                self.assertEqual(row["rt_core_status"], rt.rt_core_app_maturity(app).current_status)
                self.assertEqual(row["performance_class"], rt.optix_app_performance_support(app).performance_class)
                self.assertEqual(row["public_wording_status"], rt.rtx_public_wording_status(app).status)
                self.assertTrue(row["native_continuation_contract"])
                if row["readiness_status"] == "ready_for_rtx_claim_review":
                    self.assertTrue(row["non_claim_boundary"])

    def test_status_page_has_required_claim_commands_and_boundaries(self) -> None:
        payload = goal947.build_status_page()
        rows = {row["app"]: row for row in payload["rows"]}
        self.assertIn("--require-rt-core", rows["database_analytics"]["claim_command"])
        self.assertIn("--scenario visibility_edges", rows["graph_analytics"]["claim_command"])
        self.assertIn("goal933_prepared_segment_polygon_optix_profiler.py", rows["segment_polygon_hitcount"]["claim_command"])
        self.assertIn("goal934_prepared_segment_polygon_pair_rows_optix_profiler.py", rows["segment_polygon_anyhit_rows"]["claim_command"])
        self.assertIn("--output-mode density_count", rows["outlier_detection"]["claim_command"])
        self.assertIn("--output-mode core_count", rows["dbscan_clustering"]["claim_command"])
        self.assertIn("scalar threshold-count", rows["outlier_detection"]["rt_core_subpath"])
        self.assertIn("scalar core-count", rows["dbscan_clustering"]["rt_core_subpath"])
        self.assertEqual(rows["apple_rt_demo"]["cloud_action"], "never include in NVIDIA RTX cloud batch")
        self.assertEqual(rows["hiprt_ray_triangle_hitcount"]["cloud_action"], "never include in NVIDIA RTX cloud batch")
        for app, row in rows.items():
            with self.subTest(app=app):
                self.assertNotIn("RTDL accelerates the whole app", row["allowed_claim"])

    def test_markdown_is_public_and_links_from_docs_index_and_readme(self) -> None:
        md = (ROOT / "docs" / "v1_0_rtx_app_status.md").read_text(encoding="utf-8")
        docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("# v1.0 RTX App Status", md)
        self.assertIn("public speedup claim authorized: `False`", md)
        self.assertIn("Native-continuation contract", md)
        self.assertIn("Forbidden Wording", md)
        self.assertIn("[v1.0 RTX App Status](v1_0_rtx_app_status.md)", docs_index)
        self.assertIn("docs/v1_0_rtx_app_status.md", readme)

    def test_cli_writes_reproducible_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "status.json"
            output_md = Path(tmp) / "status.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal947_v1_rtx_app_status_page.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertEqual(payload["summary"]["ready_for_rtx_claim_review"], 16)
            self.assertEqual(payload["summary"]["reviewed_public_wording"], 11)
            self.assertIn("v1.0 RTX App Status", markdown)
            self.assertIn("Reviewed Public RTX Sub-Path Wording", markdown)
            self.assertIn("Goal1146", markdown)
            self.assertIn("Goal1126", markdown)
            self.assertIn("Goal1164", markdown)
            self.assertIn("Goal1165", markdown)
            self.assertIn("Goal1166", markdown)
            self.assertIn("Goal1177", markdown)
            self.assertIn("Goal1184", markdown)
            self.assertIn("Goal1208", markdown)
            self.assertIn("normalized per-pose", markdown)
            self.assertIn("road_hazard_screening / prepared_native_compact_summary_40k", markdown)
            self.assertIn("rtdsl.rtx_public_wording_matrix()", markdown)

    def test_latest_pod_batch_context_is_not_public_wording_promotion(self) -> None:
        payload = goal947.build_status_page()
        self.assertEqual(payload["summary"]["reviewed_public_wording"], 11)
        markdown = goal947.to_markdown(payload)
        self.assertIn("latest RTX pod batch and local follow-up completed (Goal1164/Goal1165): `True`", markdown)
        self.assertIn("next RTX pod packet accepted by 2-AI review (Goal1166): `True`", markdown)
        self.assertIn("recovered clean-source Goal1170 RTX batch accepted for external-review input (Goal1177): `True`", markdown)
        self.assertIn("newer Goal1182 RTX A4500 batch accepted for external-review input (Goal1184): `True`", markdown)
        self.assertIn("Goal1177 does not add a new reviewed public wording row", markdown)
        self.assertIn("Goal1184 does not add a new reviewed public wording row", markdown)
        self.assertIn("Goal1208 adds exactly one reviewed public wording row", markdown)
        self.assertIn("does not authorize new public wording", markdown)
        self.assertIn("reviewed public RTX sub-path wording rows: `11`", markdown)

    def test_checked_in_json_artifacts_include_public_wording_layer(self) -> None:
        for name in (
            "goal947_v1_rtx_app_status_2026-04-25.json",
            "goal947_v1_rtx_app_status_page_2026-04-25.json",
        ):
            with self.subTest(name=name):
                payload = json.loads((ROOT / "docs" / "reports" / name).read_text(encoding="utf-8"))
                self.assertEqual(
                    payload["source_of_truth"]["public_wording"],
                    "rtdsl.rtx_public_wording_matrix()",
                )
                self.assertIn(payload["summary"]["reviewed_public_wording"], (7, 9, 10, 11))
                robot = next(
                    row for row in payload["rows"] if row["app"] == "robot_collision_screening"
                )
                self.assertIn(robot["public_wording_status"], ("public_wording_blocked", "public_wording_reviewed"))
                facility = next(
                    row for row in payload["rows"] if row["app"] == "facility_knn_assignment"
                )
                self.assertIn(facility["public_wording_status"], ("public_wording_blocked", "public_wording_reviewed"))


if __name__ == "__main__":
    unittest.main()
