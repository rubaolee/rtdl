from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1190_next_rtx_pod_contract_manifest_supersession as goal1190


ROOT = Path(__file__).resolve().parents[1]


class Goal1190NextRtxPodContractManifestSupersessionTest(unittest.TestCase):
    def test_manifest_is_command_complete_but_not_pod_ready(self) -> None:
        payload = goal1190.build_manifest()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["row_count"], 6)
        self.assertEqual(payload["local_dry_run_required_count"], 6)
        self.assertFalse(payload["pod_ready_now"])
        self.assertIn("Goal1189", payload["supersedes"])

    def test_all_rows_have_baseline_and_optix_commands(self) -> None:
        payload = goal1190.build_manifest()
        for row in payload["rows"]:
            with self.subTest(app=row["app"]):
                self.assertEqual(row["status"], "local_dry_run_required")
                self.assertIn("python3", row["optix_command"])
                self.assertIn("python3", row["baseline_command"])
                self.assertTrue(row["phase_to_compare"])
                self.assertIn("whole-app speedup claim", row["boundary"])

    def test_graph_and_polygon_baselines_use_public_apps(self) -> None:
        payload = goal1190.build_manifest()
        rows = {row["app"]: row for row in payload["rows"]}
        self.assertIn("rtdl_graph_analytics_app.py --backend embree", rows["graph_analytics"]["baseline_command"])
        self.assertIn("rtdl_polygon_pair_overlap_area_rows.py --backend embree", rows["polygon_pair_overlap_area_rows"]["baseline_command"])
        self.assertIn("rtdl_polygon_set_jaccard.py --backend embree", rows["polygon_set_jaccard"]["baseline_command"])
        self.assertIn("rt_candidate_discovery_sec", rows["polygon_pair_overlap_area_rows"]["phase_to_compare"])
        self.assertIn("rt_candidate_discovery_sec", rows["polygon_set_jaccard"]["phase_to_compare"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "manifest.json"
            output_md = Path(tmp) / "manifest.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1190_next_rtx_pod_contract_manifest_supersession.py",
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
            self.assertTrue(payload["valid"])
            self.assertFalse(payload["pod_ready_now"])
            self.assertIn("Goal1190 Next RTX Pod Contract Manifest Supersession", markdown)
            self.assertIn("Do not use a paid pod yet", markdown)


if __name__ == "__main__":
    unittest.main()
