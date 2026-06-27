import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m55_librts_authorized_execution_20260623_2340"
)
DRY_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m55_librts_authorized_target_dry_run_20260623_2339"
)


class V3PhoenixM55LibRTSAuthorizedPodIntakeGateTest(unittest.TestCase):
    def test_m55_copy_back_is_complete_for_review(self) -> None:
        self.assertTrue((DRY_DIR / "summary.json").is_file())
        self.assertTrue((DRY_DIR / "README.md").is_file())
        self.assertTrue((EXEC_DIR / "summary.json").is_file())
        self.assertTrue((EXEC_DIR / "README.md").is_file())
        self.assertTrue((EXEC_DIR / "m55_execution_driver.log").is_file())

        stdout_json = list(EXEC_DIR.glob("*stdout.json"))
        stderr_txt = list(EXEC_DIR.glob("*stderr.txt"))
        preflight = list(EXEC_DIR.glob("preflight_*"))

        self.assertEqual(32, len(stdout_json))
        self.assertGreaterEqual(len(stderr_txt), 32)
        self.assertGreaterEqual(len(preflight), 12)

    def test_m55_summary_preserves_red_no_claim_boundary(self) -> None:
        summary = json.loads((EXEC_DIR / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(
            "m47_librts_stability_protocol_run_complete_not_release",
            summary["status"],
        )
        self.assertEqual([], summary["failed_checks"])
        self.assertEqual({}, summary["run_errors"])
        self.assertTrue(summary["summary"]["execute"])
        self.assertEqual(32, summary["summary"]["schedule_row_count"])

        for flag in (
            "release_authorized",
            "all_app_pod_spend_authorized",
            "focused_pod_spend_authorized_now",
            "public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "v4_work_authorized",
            "embedding_work_authorized",
            "c_abi_work_authorized",
            "true_zero_copy_claim_authorized",
        ):
            self.assertFalse(summary["claim_boundary"][flag])

        for scenario in ("optix_cold_single_shot", "embree_32768_stress"):
            result = summary["scenario_results"][scenario]
            self.assertEqual("red_failure_watch_row_open", result["m47_status_label"])
            self.assertIn(
                "set_b_control_candidate_missing",
                result["paired_samples"][0]["current_metadata_failures"],
            )
            self.assertTrue(
                all(sample["fixture_contract_matches"] for sample in result["paired_samples"])
            )
            self.assertTrue(
                all(
                    sample["current_stderr_empty"] and sample["v2_14_stderr_empty"]
                    for sample in result["paired_samples"]
                )
            )

    def test_m55_intake_and_review_packet_do_not_authorize_rerun_or_claims(self) -> None:
        intake = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md"
        ).read_text(encoding="utf-8")
        review = (
            ROOT
            / "docs"
            / "reviews"
            / "call_for_review_phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for text in (
            "red_failure_watch_row_open",
            "set_b_control_candidate_missing",
            "no V3 release",
            "no all-app benchmark run",
            "no second M47 run",
            "no public speedup wording",
            "no watch-row closure",
        ):
            self.assertIn(text, intake)
            self.assertIn(text, review)

        self.assertIn("review_requested_no_release_no_rerun_authorization", review)

    def test_m55_external_reviews_and_3ai_completion_preserve_red_no_rerun(self) -> None:
        claude = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m55_librts_authorized_pod_run_intake_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m55_goal_completion_audit_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m55_goal_completion_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")

        self.assertIn("accept_m55_valid_red_watch_rows_open_no_rerun", claude)
        self.assertIn(
            "accept_m55_goal_complete_valid_red_no_rerun_no_release",
            antigravity,
        )
        self.assertIn("m55_goal_complete_valid_red_no_rerun_no_release", consensus)
        self.assertIn("M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED", consensus)
        self.assertIn("token `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED` is consumed", consensus)
        self.assertIn("set_b_control_candidate_missing", consensus)
        self.assertIn("no second M47 run", consensus)
        self.assertIn("no watch-row closure", consensus)


if __name__ == "__main__":
    unittest.main()
