from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1009PublicRtxWordingReviewPacketTest(unittest.TestCase):
    def test_packet_combines_goal1006_and_goal1008_candidates(self) -> None:
        module = __import__(
            "scripts.goal1009_public_rtx_wording_review_packet",
            fromlist=["build_packet"],
        )
        payload = module.build_packet()
        self.assertEqual(payload["candidate_count"], 7)
        self.assertEqual(payload["blocked_count"], 1)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not edit public docs", payload["boundary"])

    def test_wording_is_scoped_and_robot_is_blocked(self) -> None:
        module = __import__(
            "scripts.goal1009_public_rtx_wording_review_packet",
            fromlist=["build_packet"],
        )
        payload = module.build_packet()
        wordings = "\n".join(row["candidate_public_wording"] for row in payload["rows"])
        self.assertIn("not a whole-app speedup claim", wordings)
        self.assertIn("not a default-mode claim", wordings)
        self.assertNotIn("robot_collision_screening", wordings)
        self.assertEqual(payload["blocked_rows"][0]["app"], "robot_collision_screening")

    def test_cli_writes_packet_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1009.json"
            output_md = Path(tmpdir) / "goal1009.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1009_public_rtx_wording_review_packet.py",
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
            self.assertIn("Goal1009 Public RTX Sub-Path Wording Review Packet", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["candidate_count"], 7)
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
