from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1909_v2_release_packet_skeleton_2026-05-13.md"


class Goal1909V2ReleasePacketSkeletonTest(unittest.TestCase):
    def test_skeleton_lists_populated_and_missing_slots(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: skeleton-blocked-consensus-and-policy-pending", text)
        for goal in ("Goal1900", "Goal1902", "Goals1903", "1905", "Goal1906", "Goal1907", "Goal1908"):
            self.assertIn(goal, text)
        self.assertIn("Hard Missing Slots", text)
        self.assertIn("Evidence Boundaries Still Required", text)
        self.assertIn("All-app rollup", text)
        self.assertIn("Goal1942", text)
        self.assertIn("final 3-AI consensus", text)
        self.assertIn("Final release action", text)
        self.assertIn("database_analytics", text)
        self.assertIn("Positive and exact-parity through 8,388,608 poses", text)

    def test_skeleton_keeps_claims_and_release_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "v2.0 release readiness",
            "broad RT-core speedup",
            "whole-application speedup",
            "arbitrary PyTorch/CuPy acceleration",
            "package-install support",
            "unconstrained true zero-copy",
        ):
            self.assertIn(phrase, text)
        self.assertIn("does not authorize v2.0", text)
        self.assertIn("does not replace final 3-AI release", text)
        self.assertIn("does not replace final 3-AI release", text)

    def test_skeleton_records_current_commands(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("scripts/goal1908_v2_local_preflight.py", text)
        self.assertIn("scripts/goal1928_robot_collision_v2_partner_perf.py", text)
        self.assertIn("scripts/goal1905_v2_partner_pod_batch_acceptance.py", text)


if __name__ == "__main__":
    unittest.main()
