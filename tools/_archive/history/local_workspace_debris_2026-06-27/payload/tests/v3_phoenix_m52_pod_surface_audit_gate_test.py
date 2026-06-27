import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3PhoenixM52PodSurfaceAuditGateTest(unittest.TestCase):
    def test_m52_whitelists_only_active_token_gated_surfaces(self) -> None:
        report = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("pod_runner_authorization_surface_audited_not_run_not_release", report)
        self.assertIn("M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED", report)
        self.assertIn("M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED", report)
        self.assertIn("All older `v3_phoenix_*pod*`", report)
        self.assertIn("historical evidence tooling", report)
        self.assertIn("Do not run historical POD scripts", report)
        self.assertIn("no paid POD spend", report)
        self.assertIn("no focused POD spend", report)

    def test_m52_saved_scan_includes_m47_and_m50_token_gates(self) -> None:
        summary_path = (
            ROOT
            / "docs"
            / "rebuild"
            / "v3"
            / "evidence"
            / "phoenix_v3_m52_pod_runner_authorization_surface_scan_20260623"
            / "summary.json"
        )
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(summary["status"], "scan_complete_no_run_not_release")
        self.assertIn(
            "scripts/v3_phoenix_m47_librts_stability_protocol.py",
            summary["token_gated_files"],
        )
        self.assertIn(
            "scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py",
            summary["token_gated_files"],
        )
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["all_app_pod_spend_authorized"])
        self.assertFalse(summary["focused_pod_spend_authorized_now"])

    def test_m52_review_packet_and_helper_are_registered(self) -> None:
        call = (
            ROOT
            / "docs"
            / "reviews"
            / "call_for_review_phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md"
        ).read_text(encoding="utf-8")
        debt = (
            ROOT
            / "docs"
            / "reviews"
            / "phoenix_v3_claude_review_debt_register_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("accept_m52_pod_surface_audit_no_run", call)
        self.assertIn("reject_m52_wrongly_authorizes_historical_runners", call)
        self.assertIn("Debt 11: M52 POD Runner Authorization Surface Audit", debt)
        self.assertIn(
            "run_claude_phoenix_v3_m52_pod_surface_audit_review_2026_06_23.ps1",
            debt,
        )


if __name__ == "__main__":
    unittest.main()
