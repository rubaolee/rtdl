from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1141RtxSingleSessionBundleTest(unittest.TestCase):
    def test_bundle_combines_current_source_and_changed_path_entries(self) -> None:
        from scripts import goal1141_rtx_single_session_bundle as goal1141

        payload = goal1141.build_bundle()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["setup_count"], 3)
        self.assertEqual(payload["summary"]["entry_count"], 11)
        self.assertEqual(payload["summary"]["goal1116_entry_count"], 5)
        self.assertEqual(payload["summary"]["goal1135_entry_count"], 6)
        setup = " ".join(" ".join(command) for command in payload["setup_commands"])
        self.assertIn("libgeos-dev", setup)
        self.assertIn("pkg-config", setup)
        self.assertIn("goal763_rtx_cloud_bootstrap_check.py", setup)
        self.assertIn("does not authorize public RTX speedup", payload["boundary"])
        self.assertIn("Do not start/stop a pod per app", payload["cloud_policy"])

    def test_shell_runner_keeps_going_and_records_status(self) -> None:
        from scripts import goal1141_rtx_single_session_bundle as goal1141

        shell = goal1141.to_shell(goal1141.build_bundle())
        self.assertIn("run_step()", shell)
        self.assertIn("goal1141_status.tsv", shell)
        self.assertIn("return 0", shell)
        self.assertIn("entry_11_goal1135_hausdorff_threshold_phase_gate", shell)
        self.assertIn("grep -q", shell)
        self.assertNotIn("shutdown", shell.lower())
        self.assertNotIn("terminate", shell.lower())

    def test_cli_writes_reproducible_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "bundle.json"
            output_md = Path(tmp) / "bundle.md"
            output_sh = Path(tmp) / "runner.sh"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1141_rtx_single_session_bundle.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--output-sh",
                    str(output_sh),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            shell = output_sh.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1141 RTX Single-Session Pod Bundle", markdown)
            self.assertIn("goal1116", markdown)
            self.assertIn("goal1135", markdown)
            self.assertIn("Goal1141 RTX single-session pod bundle", shell)
            self.assertTrue(output_sh.stat().st_mode & 0o111)


if __name__ == "__main__":
    unittest.main()
