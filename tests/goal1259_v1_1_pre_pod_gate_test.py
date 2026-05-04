from __future__ import annotations

import unittest

from scripts.goal1259_v1_1_pre_pod_gate import build_gate
from scripts.goal1259_v1_1_pre_pod_gate import to_markdown


class Goal1259V11PrePodGateTest(unittest.TestCase):
    def test_gate_is_ready_when_local_packet_and_intake_are_coherent(self) -> None:
        payload = build_gate()
        self.assertTrue(payload["ready_for_pod"])
        self.assertEqual(payload["blockers"], [])
        self.assertTrue(payload["packet"]["archive_sha_ok"])
        self.assertEqual(
            payload["packet"]["target_rows"],
            [
                "database_analytics",
                "graph_analytics",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
            ],
        )
        self.assertEqual(payload["packet"]["active_backends"], ["embree", "optix"])
        self.assertEqual(payload["packet"]["frozen_backends"], ["vulkan", "hiprt", "apple_rt"])

    def test_intake_placeholder_waits_for_pod_and_authorizes_no_wording(self) -> None:
        payload = build_gate()
        self.assertFalse(payload["intake"]["valid"])
        self.assertEqual(payload["intake"]["missing_artifact_count"], 17)
        self.assertFalse(payload["intake"]["public_wording_authorized"])

    def test_markdown_preserves_non_claim_boundary_and_next_action(self) -> None:
        text = to_markdown(build_gate())
        self.assertIn("does not run cloud", text)
        self.assertIn("authorize public RTX speedup wording", text)
        self.assertIn("Ready for pod: `True`", text)
        self.assertIn("Start one RTX Linux pod", text)


if __name__ == "__main__":
    unittest.main()
