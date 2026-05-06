from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1183_goal1182_pre_pod_readiness_gate as goal1183


ROOT = Path(__file__).resolve().parents[1]


class Goal1183Goal1182PrePodReadinessGateTest(unittest.TestCase):
    def test_gate_is_ready_and_has_no_blockers(self) -> None:
        payload = goal1183.build_gate()
        self.assertFalse(payload["ready_for_pod"])
        self.assertEqual(payload["blockers"], ["archive_exists", "archive_sha_matches_packet"])
        self.assertNotEqual(payload["archive_sha256"], payload["packet_sha256"])
        self.assertIn("Fix the listed local pre-pod blockers", payload["next_action"])

    def test_gate_requires_copyback_and_intake(self) -> None:
        payload = goal1183.build_gate()
        self.assertIn("run scripts/goal1170_clean_source_rtx_batch_intake.py", payload["post_pod_required_action"])
        self.assertTrue(payload["checks"]["copy_back_commands_cover_result_and_sha"])
        self.assertTrue(payload["checks"]["intake_script_exists"])
        self.assertIn("does not start cloud resources", payload["boundary"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "gate.json"
            output_md = Path(tmp) / "gate.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1183_goal1182_pre_pod_readiness_gate.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertFalse(payload["ready_for_pod"])
            self.assertIn("Goal1183 Goal1182 Pre-Pod Readiness Gate", markdown)
            self.assertIn("Blockers", markdown)


if __name__ == "__main__":
    unittest.main()
