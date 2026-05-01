from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal865_road_hazard_review_packet as goal865


ROOT = Path(__file__).resolve().parents[1]


def _segment_packet(status: str) -> dict[str, object]:
    return {
        "goal": "Goal864 segment/polygon gate review packet",
        "recommended_status": status,
    }


class Goal865RoadHazardReviewPacketTest(unittest.TestCase):
    def test_missing_segment_optix_artifact_blocks_road_hazard(self) -> None:
        packet = goal865.build_packet(_segment_packet("needs_real_optix_artifact"))
        self.assertEqual(packet["road_hazard_recommended_status"], "needs_segment_polygon_real_optix_artifact")
        self.assertEqual(packet["blocker"], "segment_polygon_real_optix_artifact_missing")

    def test_segment_gate_failure_blocks_road_hazard(self) -> None:
        packet = goal865.build_packet(_segment_packet("blocked_by_gate_failure"))
        self.assertEqual(packet["road_hazard_recommended_status"], "blocked_by_segment_polygon_gate_failure")

    def test_review_ready_segment_packet_allows_review_ready_road_hazard_packet(self) -> None:
        packet = goal865.build_packet(_segment_packet("ready_for_review"))
        self.assertEqual(packet["road_hazard_recommended_status"], "ready_for_review")
        self.assertEqual(packet["blocker"], "none")

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            segment_json = Path(tmp) / "segment.json"
            output_json = Path(tmp) / "road.json"
            output_md = Path(tmp) / "road.md"
            segment_json.write_text(json.dumps(_segment_packet("needs_real_optix_artifact")), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal865_road_hazard_review_packet.py",
                    "--segment-packet-json",
                    str(segment_json),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": "src:."},
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["road_hazard_recommended_status"], "needs_segment_polygon_real_optix_artifact")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
