from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1062BlockedRtxWordingRerunManifestTest(unittest.TestCase):
    def test_manifest_targets_only_remaining_blocked_public_wording_rows(self) -> None:
        module = __import__(
            "scripts.goal1062_blocked_rtx_wording_rerun_manifest",
            fromlist=["build_manifest"],
        )
        payload = module.build_manifest()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["blocked_apps"], [])
        self.assertEqual(payload["summary"]["row_count"], 0)
        self.assertEqual(payload["summary"]["validation_row_count"], 0)
        self.assertEqual(payload["summary"]["timing_row_count"], 0)
        self.assertEqual(payload["summary"]["validation_rows_with_skip_validation"], [])
        self.assertEqual(payload["summary"]["timing_rows_without_floor"], [])
        self.assertIn("does not run cloud", payload["boundary"])

    def test_validation_rows_do_not_skip_validation_and_timing_rows_have_floor(self) -> None:
        module = __import__(
            "scripts.goal1062_blocked_rtx_wording_rerun_manifest",
            fromlist=["build_manifest"],
        )
        rows = module.build_manifest()["rows"]
        self.assertEqual(rows, [])

    def test_cli_writes_json_markdown_and_shell_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1062_blocked_rtx_wording_rerun_manifest.py",
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
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1062 Blocked RTX Wording Rerun Manifest", markdown)
            self.assertNotIn("robot_prepared_pose_flags_large_timing.json", markdown)
            shell = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_SOURCE_COMMIT", shell)
            self.assertIn("nvidia-smi", shell)
            self.assertIn("Goal1062 complete", shell)


if __name__ == "__main__":
    unittest.main()
