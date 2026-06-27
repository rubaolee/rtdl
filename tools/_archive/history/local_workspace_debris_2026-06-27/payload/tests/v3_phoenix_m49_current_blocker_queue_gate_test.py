import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3PhoenixM49CurrentBlockerQueueGateTest(unittest.TestCase):
    def test_m49_reframes_old_spatial_target_without_authorizing_work(self) -> None:
        report = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("current_queue_refreshed_not_release_not_pod", report)
        self.assertIn("old M8", report)
        self.assertIn("Spatial/RayJoin", report)
        self.assertIn("stale", report)
        self.assertIn("generic topology-stream residency", report)
        self.assertIn("full-M3 accounting", report)
        self.assertIn("not a license to tune one app route", report)
        self.assertIn("no paid POD spend", report)
        self.assertIn("no all-app benchmark run", report)
        self.assertIn("no V3 release", report)

    def test_m49_review_packet_and_debt_are_registered(self) -> None:
        call = (
            ROOT
            / "docs"
            / "reviews"
            / "call_for_review_phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md"
        ).read_text(encoding="utf-8")
        debt = (
            ROOT
            / "docs"
            / "reviews"
            / "phoenix_v3_claude_review_debt_register_2026-06-23.md"
        ).read_text(encoding="utf-8")
        handoff = (
            ROOT
            / "docs"
            / "handoff"
            / "PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md"
        ).read_text(encoding="utf-8")

        self.assertIn("accept_m49_queue_refresh_no_run", call)
        self.assertIn("no paid POD spend", call)
        self.assertIn("Debt 8: M49 Current Blocker Queue After M48", debt)
        self.assertIn("run_claude_phoenix_v3_m49_current_blocker_queue_review_2026_06_23.ps1", debt)
        self.assertIn("phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md", handoff)
        self.assertIn("route tuning", handoff)


if __name__ == "__main__":
    unittest.main()
