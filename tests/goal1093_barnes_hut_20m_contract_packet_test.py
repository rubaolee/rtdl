from __future__ import annotations

import unittest

from scripts.goal1093_barnes_hut_20m_contract_packet import build_packet
from scripts.goal1093_barnes_hut_20m_contract_packet import to_shell


class Goal1093BarnesHut20mContractPacketTest(unittest.TestCase):
    def test_packet_uses_same_depth8_contract_for_validation_and_timing(self) -> None:
        packet = build_packet()
        rows = packet["rows"]

        self.assertTrue(packet["valid"])
        self.assertEqual(packet["summary"]["row_count"], 2)
        self.assertEqual(rows[0]["barnes_tree_depth"], 8)
        self.assertEqual(rows[1]["barnes_tree_depth"], 8)
        self.assertEqual(rows[0]["node_count"], 65_536)
        self.assertEqual(rows[1]["node_count"], 65_536)
        self.assertEqual(rows[0]["hit_threshold"], 4)
        self.assertEqual(rows[1]["hit_threshold"], 4)
        self.assertEqual(rows[0]["radius"], 0.1)
        self.assertEqual(rows[1]["radius"], 0.1)

    def test_validation_does_not_skip_and_timing_is_timing_only(self) -> None:
        validation, timing = build_packet()["rows"]
        validation_command = " ".join(validation["command"])
        timing_command = " ".join(timing["command"])

        self.assertTrue(validation["requires_validation"])
        self.assertFalse(validation["contains_skip_validation"])
        self.assertNotIn("--skip-validation", validation_command)
        self.assertFalse(timing["requires_validation"])
        self.assertTrue(timing["contains_skip_validation"])
        self.assertIn("--skip-validation", timing_command)
        self.assertEqual(timing["timing_floor_sec"], 0.100)

    def test_runner_and_boundary_do_not_authorize_claims(self) -> None:
        packet = build_packet()
        runner = to_shell(packet)

        self.assertEqual(packet["summary"]["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not authorize public RTX speedup claims", packet["boundary"])
        self.assertIn("RTDL_SOURCE_COMMIT", runner)
        self.assertIn("nvidia-smi", runner)
        self.assertIn("barnes_hut_depth8_4096_validation.json", runner)
        self.assertIn("barnes_hut_depth8_20m_timing.json", runner)


if __name__ == "__main__":
    unittest.main()
