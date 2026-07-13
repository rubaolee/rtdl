from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json"
)


class Goal5281NativeHeavyOffloadTelemetryArtifactTest(unittest.TestCase):
    def test_pod_artifact_contains_v2_heavy_offload_telemetry(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            data["schema"],
            "rtdl.paper_reproduction.xhd.goal5281.native_heavy_offload_telemetry_pod.v1",
        )
        self.assertTrue(data["matched"])
        self.assertTrue(data["native_memory_telemetry_collected"])
        self.assertGreater(data["offload_row_count_from_rows"], 0)
        self.assertEqual(data["frontier_kind_codes"], [2, 2, 2, 2, 2, 2])

        telemetry = data["native_memory_telemetry"]
        self.assertEqual(
            telemetry["schema"],
            "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v2",
        )
        self.assertEqual(
            telemetry["heavy_offload_peak_rows"],
            data["offload_row_count_from_rows"],
        )
        self.assertEqual(
            telemetry["heavy_offload_queue_peak_bytes"],
            data["offload_row_count_from_rows"] * 2 * 8,
        )
        self.assertEqual(telemetry["miss_queue_capacity"], 0)
        self.assertIn("not an author Figure 11 parity claim", telemetry["heavy_offload_semantics"])

    def test_pod_artifact_keeps_figure11_claims_unauthorized(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = data["boundary"]
        self.assertFalse(boundary["figure11_reproduced"])
        self.assertFalse(boundary["author_memory_parity_claimed"])
        self.assertFalse(boundary["performance_claim_authorized"])
        self.assertIn("not X-HD Figure 11 reproduction", boundary["note"])


if __name__ == "__main__":
    unittest.main()
