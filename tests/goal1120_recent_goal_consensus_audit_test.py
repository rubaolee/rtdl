from __future__ import annotations

import unittest


class Goal1120RecentGoalConsensusAuditTest(unittest.TestCase):
    def test_recent_goals_have_consensus_artifacts(self) -> None:
        module = __import__("scripts.goal1120_recent_goal_consensus_audit", fromlist=["build_audit"])
        payload = module.build_audit()

        self.assertTrue(payload["valid"], payload["summary"]["blockers"])
        self.assertEqual(payload["summary"]["goal_count"], 20)
        self.assertEqual(payload["summary"]["closed_count"], 20)
        self.assertEqual(payload["summary"]["blockers"], [])

    def test_audit_rows_include_report_review_and_consensus(self) -> None:
        module = __import__("scripts.goal1120_recent_goal_consensus_audit", fromlist=["build_audit"])
        rows = module.build_audit()["rows"]

        for row in rows:
            self.assertTrue(row["primary_report"], row)
            self.assertTrue(row["external_review"], row)
            self.assertTrue(row["two_ai_consensus"], row)
            self.assertTrue(row["closed"], row)


if __name__ == "__main__":
    unittest.main()
