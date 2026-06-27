import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRY_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m58_librts_m57_authorized_target_dry_run_20260624_0054"
)
EXEC_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m58_librts_m57_authorized_execution_20260624_0055"
)


class V3PhoenixM58LibRTSAuthorizedRerunIntakeGateTest(unittest.TestCase):
    def test_m58_dry_run_executed_source_signature_preflight(self) -> None:
        summary = json.loads((DRY_DIR / "summary.json").read_text(encoding="utf-8"))
        source_stdout = json.loads(
            (DRY_DIR / "preflight_current_librts_set_b_source_signature.stdout.txt").read_text(
                encoding="utf-8"
            )
        )
        source_row = summary["preflight"]["current_librts_set_b_source_signature"]

        self.assertEqual(
            "m47_librts_stability_protocol_preflight_only_no_pod_not_release",
            summary["status"],
        )
        self.assertFalse(summary["summary"]["execute"])
        self.assertTrue(summary["summary"]["run_preflight"])
        self.assertEqual([], summary["failed_checks"])
        self.assertEqual(0, source_row["returncode"])
        self.assertEqual([], source_stdout["failed"])
        self.assertTrue(all(source_stdout["checks"].values()))

    def test_m58_execution_valid_yellow_open_with_metadata_cleared(self) -> None:
        summary = json.loads((EXEC_DIR / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(
            "m47_librts_stability_protocol_run_complete_not_release",
            summary["status"],
        )
        self.assertEqual([], summary["failed_checks"])
        self.assertEqual({}, summary["run_errors"])
        self.assertTrue(summary["summary"]["execute"])
        self.assertFalse(summary["summary"]["run_preflight"])

        scenarios = summary["scenario_results"]
        self.assertEqual(
            "yellow_stability_boundary_watch_row_open",
            scenarios["embree_32768_stress"]["m47_status_label"],
        )
        self.assertEqual(
            "yellow_stability_boundary_watch_row_open",
            scenarios["optix_cold_single_shot"]["m47_status_label"],
        )
        for result in scenarios.values():
            self.assertTrue(
                all(not row["current_metadata_failures"] for row in result["paired_samples"])
            )
            self.assertTrue(
                all(row["fixture_contract_matches"] for row in result["paired_samples"])
            )

        self.assertEqual(32, len(list(EXEC_DIR.glob("*stdout.json"))))
        self.assertGreaterEqual(len(list(EXEC_DIR.glob("*stderr.txt"))), 32)

    def test_m58_intake_and_review_packet_preserve_no_closure(self) -> None:
        intake = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m58_librts_m57_authorized_pod_rerun_intake_2026-06-23.md"
        ).read_text(encoding="utf-8")
        review = (
            ROOT
            / "docs"
            / "reviews"
            / "call_for_review_phoenix_v3_m58_librts_m57_authorized_pod_rerun_intake_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for text in (intake, review):
            self.assertIn("yellow_stability_boundary_watch_row_open", text)
            self.assertIn("no watch-row closure", text)
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark run", text)
            self.assertIn("no public speedup wording", text)
            self.assertNotIn("release_ready", text)

    def test_m58_external_reviews_and_consensus_accept_yellow_open_only(self) -> None:
        claude = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m58_librts_authorized_rerun_intake_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m58_librts_authorized_rerun_intake_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m58_rerun_intake_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")
        audit = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m58_goal_completion_audit_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for text in (claude, antigravity, consensus, audit):
            self.assertIn("accept_m58_valid_yellow_watch_rows_open_no_closure", text)
            self.assertIn("yellow_stability_boundary_watch_row_open", text)
            self.assertIn("no watch-row closure", text)
            self.assertIn("no V3 release", text)
            self.assertIn("no public speedup wording", text)
            self.assertNotIn("release_ready", text)

        self.assertIn("m58_valid_yellow_watch_rows_open_no_closure", consensus)
        self.assertIn("m58_goal_complete_valid_yellow_open_no_closure", audit)


if __name__ == "__main__":
    unittest.main()
