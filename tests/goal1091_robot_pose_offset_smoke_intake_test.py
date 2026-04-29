from __future__ import annotations

import unittest

from scripts.goal1091_robot_pose_offset_smoke_intake import build_intake
from scripts.goal1091_robot_pose_offset_smoke_intake import to_markdown


class Goal1091RobotPoseOffsetSmokeIntakeTest(unittest.TestCase):
    def test_smoke_artifact_validates_pose_offset_path(self) -> None:
        intake = build_intake()

        self.assertTrue(intake["valid"])
        self.assertEqual(intake["status"], "ok")
        self.assertTrue(all(intake["checks"].values()))
        self.assertFalse(intake["public_speedup_claim_authorized"])
        self.assertGreaterEqual(min(intake["summary"]["colliding_pose_ids_sample"]), 200001)

    def test_markdown_keeps_no_claim_boundary(self) -> None:
        markdown = to_markdown(build_intake())

        self.assertIn("does not run the heavy 36M baseline", markdown)
        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("pose_id_start_recorded", markdown)


if __name__ == "__main__":
    unittest.main()
