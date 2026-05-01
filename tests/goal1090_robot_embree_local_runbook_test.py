from __future__ import annotations

import unittest

from scripts.goal1090_robot_embree_local_runbook import build_runbook
from scripts.goal1090_robot_embree_local_runbook import to_markdown


class Goal1090RobotEmbreeLocalRunbookTest(unittest.TestCase):
    def test_runbook_is_non_cloud_and_claim_safe(self) -> None:
        runbook = build_runbook()

        self.assertTrue(runbook["valid"])
        self.assertTrue(runbook["not_pod_work"])
        self.assertEqual(runbook["host_policy"], "non_cloud_linux_or_windows_preferred")
        self.assertEqual(runbook["summary"]["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not create cloud resources", runbook["boundary"])
        self.assertIn("does not authorize public RTX speedup claims", runbook["boundary"])

    def test_runbook_contains_resumable_runner_and_intake_steps(self) -> None:
        runbook = build_runbook()
        commands = "\n".join(step["command"] for step in runbook["steps"])

        self.assertIn("goal1085_robot_chunked_embree_baseline_runner.sh", commands)
        self.assertIn("goal1086_robot_chunked_embree_baseline_intake.py", commands)
        self.assertIn("RTDL_GOAL1085_START_CHUNK=0", commands)
        self.assertIn("RTDL_GOAL1085_END_CHUNK=0", commands)
        self.assertIn("RTDL_GOAL1085_SKIP_EXISTING=1", commands)

    def test_scale_contract_records_pose_id_formula(self) -> None:
        runbook = build_runbook()
        scale = runbook["scale_contract"]

        self.assertEqual(scale["total_pose_count"], 36_000_000)
        self.assertEqual(scale["chunk_count"], 180)
        self.assertEqual(scale["chunk_pose_count"], 200_000)
        self.assertEqual(scale["obstacle_count"], 4096)
        self.assertEqual(scale["pose_id_start_formula"], "chunk_index * 200000 + 1")
        self.assertIn("RTDL_GOAL1085_SKIP_EXISTING", scale["resume_controls"])

    def test_markdown_is_user_executable(self) -> None:
        markdown = to_markdown(build_runbook())

        self.assertIn("Goal1090 Robot Embree Local Baseline Runbook", markdown)
        self.assertIn("goal1085_robot_chunked_embree_baseline_runner.sh", markdown)
        self.assertIn("goal1086_robot_chunked_embree_baseline_intake.py", markdown)
        self.assertIn("Not pod work", markdown)


if __name__ == "__main__":
    unittest.main()
