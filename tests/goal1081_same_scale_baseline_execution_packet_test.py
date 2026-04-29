from __future__ import annotations

import unittest

from scripts.goal1081_same_scale_baseline_execution_packet import build_packet
from scripts.goal1081_same_scale_baseline_execution_packet import to_markdown


class Goal1081SameScaleBaselineExecutionPacketTest(unittest.TestCase):
    def test_packet_is_valid_and_authorizes_no_public_speedup_claims(self) -> None:
        packet = build_packet()

        self.assertTrue(packet["valid"])
        self.assertEqual(packet["summary"]["row_count"], 3)
        self.assertEqual(packet["summary"]["executable_row_count"], 2)
        self.assertEqual(packet["summary"]["public_speedup_claim_authorized_count"], 0)
        self.assertTrue(
            all(not row["public_speedup_claim_authorized"] for row in packet["rows"])
        )
        self.assertTrue(all(row["required_before_public_wording"] for row in packet["rows"]))

    def test_facility_baseline_matches_rtx_scale(self) -> None:
        packet = build_packet()
        facility = packet["rows"][0]
        command = " ".join(facility["command"])

        self.assertEqual(facility["app"], "facility_knn_assignment")
        self.assertEqual(facility["baseline_kind"], "cpu_oracle_same_scale")
        self.assertEqual(facility["scale"]["copies"], 2_500_000)
        self.assertIn("--copies 2500000", command)
        self.assertIn("facility_coverage_threshold_2_5m_cpu_oracle.json", command)

    def test_robot_baseline_matches_rtx_scale(self) -> None:
        packet = build_packet()
        robot = packet["rows"][1]
        command = " ".join(robot["command"])

        self.assertEqual(robot["app"], "robot_collision_screening")
        self.assertEqual(robot["baseline_kind"], "embree_same_scale")
        self.assertEqual(robot["scale"]["pose_count"], 36_000_000)
        self.assertEqual(robot["scale"]["obstacle_count"], 4096)
        self.assertIn("--pose-count 36000000", command)
        self.assertIn("--obstacle-count 4096", command)
        self.assertIn("--worker-count 8", command)

    def test_barnes_hut_is_not_executable_until_contract_is_superseded(self) -> None:
        packet = build_packet()
        barnes_hut = packet["rows"][2]

        self.assertEqual(barnes_hut["app"], "barnes_hut_force_app")
        self.assertEqual(barnes_hut["baseline_kind"], "future_contract")
        self.assertEqual(barnes_hut["recommended_host"], "not_ready")
        self.assertEqual(barnes_hut["command"], [])
        self.assertIn("not ready", to_markdown(packet))


if __name__ == "__main__":
    unittest.main()
