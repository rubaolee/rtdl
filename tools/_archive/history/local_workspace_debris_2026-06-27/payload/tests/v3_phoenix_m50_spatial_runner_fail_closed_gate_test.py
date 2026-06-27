import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3PhoenixM50SpatialRunnerFailClosedGateTest(unittest.TestCase):
    def test_m50_report_and_review_packet_preserve_no_run_boundary(self) -> None:
        report = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md"
        ).read_text(encoding="utf-8")
        call = (
            ROOT
            / "docs"
            / "reviews"
            / "call_for_review_phoenix_v3_m50_spatial_topology_runner_fail_closed_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("m50_spatial_topology_runner_fail_closed_not_pod_not_release", report)
        self.assertIn("defaults to a dry-run packet", report)
        self.assertIn("M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED", report)
        self.assertIn("no paid POD spend", report)
        self.assertIn("no focused POD spend", report)
        self.assertIn("no V3 release", report)
        self.assertIn("accept_m50_runner_fail_closed_no_run", call)
        self.assertIn("reject_m50_runner_still_runs_too_easily", call)
        self.assertIn("no focused POD spend", call)

    def test_m50_runner_and_debt_are_registered(self) -> None:
        runner = (
            ROOT
            / "scripts"
            / "v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py"
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

        self.assertIn("STATUS_DRY_RUN", runner)
        self.assertIn("planned_execution_requires_token", runner)
        self.assertIn("requires_explicit_authorization", runner)
        self.assertIn("Debt 9: M50 Spatial Topology-Stream Runner Fail-Closed Gate", debt)
        self.assertIn(
            "run_claude_phoenix_v3_m50_spatial_topology_runner_fail_closed_review_2026_06_23.ps1",
            debt,
        )
        self.assertIn("phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md", handoff)
        self.assertIn("dry-run by default", handoff)


if __name__ == "__main__":
    unittest.main()
