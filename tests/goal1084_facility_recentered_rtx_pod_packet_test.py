from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1084FacilityRecenteredRtxPodPacketTest(unittest.TestCase):
    def test_packet_has_single_validated_recentered_row(self) -> None:
        module = __import__("scripts.goal1084_facility_recentered_rtx_pod_packet", fromlist=["build_packet"])
        payload = module.build_packet()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 1)
        self.assertEqual(payload["summary"]["validation_row_count"], 1)
        self.assertEqual(payload["summary"]["rows_with_skip_validation"], [])
        self.assertEqual(payload["summary"]["public_speedup_claim_authorized_count"], 0)

        row = payload["rows"][0]
        command = " ".join(row["command"])
        self.assertIn("facility_service_coverage_recentered", command)
        self.assertIn("--copies 2500000", command)
        self.assertNotIn("--skip-validation", command)
        self.assertEqual(row["timing_floor_sec"], 0.100)

    def test_cli_writes_json_markdown_and_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "packet.json"
            output_md = Path(tmpdir) / "packet.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1084_facility_recentered_rtx_pod_packet.py",
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
                stderr=subprocess.PIPE,
            )
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1084 Facility Recentered RTX Pod Packet", output_md.read_text(encoding="utf-8"))
            runner = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_SOURCE_COMMIT", runner)
            self.assertIn("nvidia-smi", runner)
            self.assertIn("facility_service_coverage_recentered", runner)
            self.assertNotIn("--skip-validation", runner)


if __name__ == "__main__":
    unittest.main()
