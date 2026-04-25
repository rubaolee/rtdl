from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md"
MATRIX = ROOT / "docs" / "app_engine_support_matrix.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal830_two_ai_consensus_2026-04-23.md"


class Goal830RtxGoalSequenceDocSyncTest(unittest.TestCase):
    def test_goal_sequence_matches_completed_827_to_829_work(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("Goal827: fail closed on incomplete post-cloud artifacts", text)
        self.assertIn("Goal828: add deferred/filter controls to the one-shot pod runner", text)
        self.assertIn("Goal829: publish the single-session cloud runbook", text)
        self.assertIn("Goal830+: return to segment/polygon strict packaging", text)
        self.assertNotIn("Goal827: complete segment/polygon native OptiX strict-gate packaging", text)

    def test_exit_criteria_link_single_session_runbook(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("docs/rtx_cloud_single_session_runbook.md", text)
        self.assertIn("no per-app restart/stop loop", text)

    def test_support_matrix_links_paid_pod_runbook(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")

        self.assertIn("/Users/rl2025/rtdl_python_only/docs/rtx_cloud_single_session_runbook.md", text)
        self.assertIn("Goal824 local readiness first", text)
        self.assertIn("run the OOM-safe groups", text)
        self.assertIn("copy artifacts after every group", text)

    def test_two_ai_consensus_is_recorded_without_claiming_claude(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Codex | ACCEPT", text)
        self.assertIn("Gemini 2.5 Flash | ACCEPT", text)
        self.assertIn("Claude | unavailable", text)
        self.assertIn("2-AI consensus is achieved by Codex + Gemini", text)
        self.assertIn("no verdict claimed", text)


if __name__ == "__main__":
    unittest.main()
