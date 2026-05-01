from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1076BarnesHutRichRtxPodCandidateTest(unittest.TestCase):
    def test_manifest_has_separate_validation_and_timing_rows(self) -> None:
        module = __import__("scripts.goal1076_barnes_hut_rich_rtx_pod_candidate", fromlist=["build_manifest"])
        payload = module.build_manifest()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 2)
        self.assertEqual(payload["summary"]["validation_row_count"], 1)
        self.assertEqual(payload["summary"]["timing_row_count"], 1)
        self.assertEqual(payload["summary"]["validation_rows_with_skip_validation"], [])
        self.assertEqual(payload["summary"]["timing_rows_without_floor"], [])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_rows_use_rich_contract_scales(self) -> None:
        module = __import__("scripts.goal1076_barnes_hut_rich_rtx_pod_candidate", fromlist=["build_manifest"])
        rows = module.build_manifest()["rows"]
        validation = next(row for row in rows if row["phase"] == "correctness_validation")
        timing = next(row for row in rows if row["phase"] == "large_timing_repeat")

        self.assertFalse(validation["contains_skip_validation"])
        self.assertIn("1024", validation["command"])
        self.assertIn("--barnes-tree-depth", validation["command"])
        self.assertIn("6", validation["command"])
        self.assertIn("--hit-threshold", validation["command"])
        self.assertIn("4", validation["command"])

        self.assertTrue(timing["contains_skip_validation"])
        self.assertEqual(timing["timing_floor_sec"], 0.100)
        self.assertIn("1000000", timing["command"])
        self.assertIn("8", timing["command"])
        self.assertIn("4", timing["command"])

    def test_cli_writes_manifest_markdown_and_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1076_barnes_hut_rich_rtx_pod_candidate.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--output-sh",
                    str(output_sh),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["row_count"], 2)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1076 Barnes-Hut Rich RTX Pod Candidate", markdown)
            runner = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_SOURCE_COMMIT", runner)
            self.assertIn("nvidia-smi", runner)
            self.assertIn("--barnes-tree-depth 8", runner)
            self.assertIn("--hit-threshold 4", runner)


if __name__ == "__main__":
    unittest.main()
