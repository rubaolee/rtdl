from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1066RejectedRtxLocalRemediationManifestTest(unittest.TestCase):
    def test_manifest_covers_all_rejected_goal1063_rows(self) -> None:
        module = __import__(
            "scripts.goal1066_rejected_rtx_local_remediation_manifest",
            fromlist=["build_manifest"],
        )
        payload = module.build_manifest()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["rejected_row_count"], 8)
        self.assertEqual(payload["missing_remediation"], [])
        self.assertEqual(
            payload["remediation_class_counts"],
            {
                "chunking_and_candidate_discovery": 2,
                "code_path_profile": 3,
                "rt_mapping_profile": 1,
                "scale_contract_repair": 2,
            },
        )
        self.assertIn("does not run cloud", payload["boundary"])

    def test_every_row_blocks_pod_until_local_acceptance(self) -> None:
        module = __import__(
            "scripts.goal1066_rejected_rtx_local_remediation_manifest",
            fromlist=["build_manifest"],
        )
        for row in module.build_manifest()["rows"]:
            with self.subTest(app=row["app"], path=row["path_name"]):
                self.assertTrue(row["pod_policy"].startswith("no_pod_until"))
                self.assertTrue(row["local_probe_commands"])
                self.assertTrue(row["acceptance_before_pod"])
                self.assertIn("PYTHONPATH=src:.", row["local_probe_commands"][0])

    def test_specific_rows_have_correct_local_strategy(self) -> None:
        module = __import__(
            "scripts.goal1066_rejected_rtx_local_remediation_manifest",
            fromlist=["build_manifest"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_manifest()["rows"]
        }
        self.assertEqual(
            rows[("hausdorff_distance", "directed_threshold_prepared")]["remediation_class"],
            "scale_contract_repair",
        )
        self.assertIn(
            "goal887_prepared_decision_phase_profiler.py",
            rows[("hausdorff_distance", "directed_threshold_prepared")]["local_probe_commands"][0],
        )
        self.assertEqual(
            rows[("polygon_set_jaccard", "polygon_set_jaccard_optix_native_assisted_phase_gate")][
                "remediation_class"
            ],
            "chunking_and_candidate_discovery",
        )
        self.assertEqual(
            rows[("graph_analytics", "graph_visibility_edges_gate")]["remediation_class"],
            "rt_mapping_profile",
        )

    def test_cli_writes_manifest_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1066_rejected_rtx_local_remediation_manifest.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["rejected_row_count"], 8)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1066 Rejected RTX Local Remediation Manifest", markdown)
            self.assertIn("no_pod_until_code_or_scale_changes", markdown)


if __name__ == "__main__":
    unittest.main()
