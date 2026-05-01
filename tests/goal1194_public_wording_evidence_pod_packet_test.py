from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1194_public_wording_evidence_pod_packet as goal1194


ROOT = Path(__file__).resolve().parents[1]


class Goal1194PublicWordingEvidencePodPacketTest(unittest.TestCase):
    def test_packet_builds_archive_and_goal1192_goal1193_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.tar.gz"
            payload = goal1194.build_packet(archive)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["pod_batch"]["expected_artifacts"], 12)
        self.assertEqual(payload["pod_batch"]["expected_app_pairs"], 6)
        self.assertIn("goal1192_public_wording_evidence_batch_runner.sh", payload["pod_batch"]["runner"])
        self.assertIn("goal1193_public_wording_evidence_batch_intake.py", payload["pod_batch"]["intake"])
        self.assertIn("EXPECTED_SHA256=" + payload["archive"]["archive_sha256"], payload["commands"]["run_on_pod"])
        self.assertIn("goal1194_executor.sh", "\n".join(payload["commands"]["upload"]))
        self.assertIn("goal1193_public_wording_evidence_batch_intake.py", "\n".join(payload["commands"]["copy_back_and_intake"]))
        self.assertIn("does not run cloud", payload["boundary"])

    def test_executor_contains_required_setup_and_boundaries(self) -> None:
        text = (ROOT / "scripts/goal1194_public_wording_evidence_pod_executor.sh").read_text(encoding="utf-8")
        self.assertIn("libgeos-dev", text)
        self.assertIn("make build-optix", text)
        self.assertIn("goal1192_public_wording_evidence_batch_runner.sh", text)
        self.assertIn("RTDL_SOURCE_COMMIT", text)
        self.assertIn("does not authorize public", text)

    def test_cli_writes_packet_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            archive = tmp_path / "source.tar.gz"
            output_json = tmp_path / "packet.json"
            output_md = tmp_path / "packet.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1194_public_wording_evidence_pod_packet.py",
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
            self.assertIn("Goal1194 Public Wording Evidence Pod Packet", markdown)
            self.assertIn("Copy Back And Intake", markdown)


if __name__ == "__main__":
    unittest.main()
