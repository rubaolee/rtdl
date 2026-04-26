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
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])

        rows = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), set(rt.public_apps()))
        for app, row in rows.items():
            with self.subTest(app=app):
                self.assertEqual(row["readiness_status"], rt.optix_app_benchmark_readiness(app).status)
                self.assertEqual(row["rt_core_status"], rt.rt_core_app_maturity(app).current_status)
                self.assertEqual(row["performance_class"], rt.optix_app_performance_support(app).performance_class)
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
            self.assertEqual(payload["summary"]["ready_for_rtx_claim_review"], 16)
            self.assertIn("v1.0 RTX App Status", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
