from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1182_next_pod_packet as goal1182


ROOT = Path(__file__).resolve().parents[1]


class Goal1182NextPodPacketTest(unittest.TestCase):
    def test_packet_builds_current_archive_and_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.tar.gz"
            payload = goal1182.build_packet(archive)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["pod_batch"]["expected_rows"], 8)
        self.assertEqual(len(payload["archive"]["archive_sha256"]), 64)
        self.assertIn("EXPECTED_SHA256=" + payload["archive"]["archive_sha256"], payload["commands"]["run_on_pod"])
        self.assertIn("goal1182_executor.sh", "\n".join(payload["commands"]["upload"]))
        self.assertIn("does not run cloud benchmarks", payload["boundary"])

    def test_cli_writes_packet_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.tar.gz"
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1182_next_pod_packet.py",
                    "--archive",
                    str(archive),
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
            self.assertIn("Goal1182 Next Consolidated RTX Pod Packet", markdown)
            self.assertIn("Run On Pod", markdown)


if __name__ == "__main__":
    unittest.main()
