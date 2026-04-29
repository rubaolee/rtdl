from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1085RobotChunkedEmbreeBaselinePacketTest(unittest.TestCase):
    def test_packet_splits_36m_robot_baseline_into_180_chunks(self) -> None:
        module = __import__("scripts.goal1085_robot_chunked_embree_baseline_packet", fromlist=["build_packet"])
        payload = module.build_packet()
        scale = payload["scale"]

        self.assertTrue(payload["valid"])
        self.assertEqual(scale["total_pose_count"], 36_000_000)
        self.assertEqual(scale["chunk_pose_count"], 200_000)
        self.assertEqual(scale["chunk_count"], 180)
        self.assertEqual(scale["obstacle_count"], 4096)
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertIn("same-total-work engineering baseline", payload["baseline_interpretation"])

    def test_cli_writes_runner_without_running_heavy_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "packet.json"
            output_md = Path(tmpdir) / "packet.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1085_robot_chunked_embree_baseline_packet.py",
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
            self.assertEqual(payload["scale"]["chunk_count"], 180)
            self.assertIn("RTDL_GOAL1085_START_CHUNK", payload["baseline_interpretation"])
            runner = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_GOAL1085_START_CHUNK", runner)
            self.assertIn("RTDL_GOAL1085_END_CHUNK", runner)
            self.assertIn("RTDL_GOAL1085_SKIP_EXISTING", runner)
            self.assertIn('seq "${RTDL_GOAL1085_START_CHUNK}" "${RTDL_GOAL1085_END_CHUNK}"', runner)
            self.assertIn("--backend embree", runner)
            self.assertIn("--pose-count 200000", runner)
            self.assertIn("--obstacle-count 4096", runner)
            self.assertIn('chunk_${chunk_index}.json', runner)


if __name__ == "__main__":
    unittest.main()
