from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4031_partition_convergence_preview_chain_packet_2026-06-08.md"
ESTIMATE = ROOT / "docs" / "reports" / "goal4026_partition_convergence_root_work_estimate.json"


class Goal4031PartitionConvergencePreviewChainPacketTest(unittest.TestCase):
    def test_packet_records_proven_and_unproven_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4019",
            "Goal4021",
            "Goal4027",
            "Goal4029",
            "Goal4032",
            "CuPy executable preview",
            "device_bounded_offsets",
            "Numba CUDA device-column preview",
            "No fast native partition-summary producer exists yet",
            "candidate_requires_native_implementation",
            "not a timing claim",
            "No speedup",
        ):
            self.assertIn(fragment, text)

    def test_estimate_artifact_and_front_door_metadata_are_consistent(self) -> None:
        self.assertTrue(ESTIMATE.exists())
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        goals = description["candidate_strategy_evidence_goals"]["partition_convergence_hybrid"]
        for goal in ("Goal4019", "Goal4021", "Goal4023", "Goal4024", "Goal4027", "Goal4029", "Goal4032"):
            self.assertIn(goal, goals)
        guidance = description["candidate_strategy_partition_guidance"]["partition_convergence_hybrid"]
        self.assertEqual(
            guidance["native_promotion_gate"],
            "candidate_device_producer_must_pass_goal4019_goal4021_goal4023_goal4024_before_timing",
        )


if __name__ == "__main__":
    unittest.main()
