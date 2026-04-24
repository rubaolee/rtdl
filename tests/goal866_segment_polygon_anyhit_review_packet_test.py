from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal866_segment_polygon_anyhit_review_packet as goal866


ROOT = Path(__file__).resolve().parents[1]


def _segment_packet(status: str) -> dict[str, object]:
    return {
        "goal": "Goal864 segment/polygon gate review packet",
        "recommended_status": status,
    }


class Goal866SegmentPolygonAnyhitReviewPacketTest(unittest.TestCase):
    def test_compact_modes_wait_for_real_segment_optix_artifact(self) -> None:
        packet = goal866.build_packet(_segment_packet("needs_real_optix_artifact"))
        self.assertEqual(
            packet["compact_modes"]["segment_counts"]["recommended_status"],
            "needs_segment_polygon_real_optix_artifact",
        )
        self.assertEqual(packet["rows_mode"]["recommended_status"], "needs_native_pair_row_emitter")

    def test_compact_modes_can_become_ready_for_review(self) -> None:
        packet = goal866.build_packet(_segment_packet("ready_for_review"))
        self.assertEqual(packet["compact_modes"]["segment_flags"]["recommended_status"], "ready_for_review")
        self.assertEqual(packet["rows_mode"]["recommended_status"], "needs_native_pair_row_emitter")

    def test_gate_failure_propagates_to_compact_modes(self) -> None:
        packet = goal866.build_packet(_segment_packet("blocked_by_gate_failure"))
        self.assertEqual(
            packet["compact_modes"]["segment_flags"]["recommended_status"],
            "blocked_by_segment_polygon_gate_failure",
        )

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            segment_json = Path(tmp) / "segment.json"
            output_json = Path(tmp) / "anyhit.json"
            output_md = Path(tmp) / "anyhit.md"
            segment_json.write_text(json.dumps(_segment_packet("needs_real_optix_artifact")), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal866_segment_polygon_anyhit_review_packet.py",
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
            self.assertEqual(payload["rows_status"], "needs_native_pair_row_emitter")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
