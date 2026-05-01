from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1189_next_rtx_pod_contract_manifest as goal1189


ROOT = Path(__file__).resolve().parents[1]


class Goal1189NextRtxPodContractManifestTest(unittest.TestCase):
    def test_manifest_is_valid_but_not_pod_ready(self) -> None:
        payload = goal1189.build_manifest()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["row_count"], 6)
        self.assertEqual(payload["pod_ready_after_local_dry_run_count"], 3)
        self.assertEqual(payload["needs_baseline_harness_count"], 3)
        self.assertIn("Do not run the next public-wording pod batch yet", payload["pod_recommendation"])

    def test_ready_and_needs_harness_apps_are_expected(self) -> None:
        payload = goal1189.build_manifest()
        self.assertEqual(
            set(payload["ready_apps"]),
            {"database_analytics", "road_hazard_screening", "hausdorff_distance"},
        )
        self.assertEqual(
            set(payload["needs_harness_apps"]),
            {"graph_analytics", "polygon_pair_overlap_area_rows", "polygon_set_jaccard"},
        )

    def test_each_row_has_boundaries_and_commands(self) -> None:
        payload = goal1189.build_manifest()
        for row in payload["rows"]:
            with self.subTest(app=row["app"]):
                self.assertIn("python3", row["optix_command"])
                self.assertIn("claim", row["boundary"])
                self.assertNotIn("whole-app speedup claim", row["claim_contract"])
                if row["status"] == "pod_ready_after_local_dry_run":
                    self.assertIn("python3", row["baseline_command"])
                else:
                    self.assertEqual(row["baseline_command"], "")
                    self.assertIn("baseline", row["missing_work"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "manifest.json"
            output_md = Path(tmp) / "manifest.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1189_next_rtx_pod_contract_manifest.py",
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
            self.assertIn("Goal1189 Next RTX Pod Contract Manifest", markdown)
            self.assertIn("needs baseline harness: `3`", markdown)
            self.assertIn("does not authorize public", markdown)


if __name__ == "__main__":
    unittest.main()
