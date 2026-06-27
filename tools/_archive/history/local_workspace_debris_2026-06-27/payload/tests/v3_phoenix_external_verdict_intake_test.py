import tempfile
import unittest
from pathlib import Path

from scripts import v3_phoenix_external_verdict_intake as intake


TEMPLATE = intake.ROOT / "docs" / "reviews" / "phoenix_v3_external_verdict_response_template_2026-06-22.md"
REVIEW_REQUEST = (
    intake.ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md"
)
CORE_GAPS_REVIEW = (
    intake.ROOT / "docs" / "reviews" / "claude_phoenix_v3_external_review_2026-06-22.md"
)
CORE_GAPS_INTAKE = (
    intake.ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json"
)
CORE_GAPS_STATUS = (
    intake.ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md"
)
SET_A_SET_B_PROPOSAL = (
    intake.ROOT / "docs" / "reviews" / "phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md"
)


class V3PhoenixExternalVerdictIntakeTest(unittest.TestCase):
    def test_default_current_records_accept_claude_release_ready_and_reject_fallbacks(self):
        payload = intake.build_payload()
        self.assertEqual(payload["tool"], "v3_phoenix_external_verdict_intake")
        self.assertEqual(payload["status"], "external_verdict_obtained")
        self.assertTrue(payload["valid_external_verdict_obtained"])
        self.assertTrue(payload["scoped_packet_authorized"])
        self.assertFalse(payload["release_authorized"])
        self.assertEqual(payload["accepted_verdict"], "release_ready")
        self.assertEqual(payload["status_line"], "external_verdict_obtained_claude_release_ready")
        self.assertEqual(len(payload["accepted_candidates"]), 1)
        self.assertEqual(payload["accepted_candidates"][0]["candidate_id"], "claude_after_dossier_release_ready")

        rejections = {item["candidate_id"]: item for item in payload["current_rejections"]}
        self.assertEqual(
            set(rejections),
            {
                "latest_external_blocked_record",
                "codex_subagent_review",
                "codex_fallback_consensus",
            },
        )
        self.assertIn(
            "external_review_not_obtained_marker",
            rejections["latest_external_blocked_record"]["reasons"],
        )
        self.assertIn(
            "bounded_timeout_record",
            rejections["latest_external_blocked_record"]["reasons"],
        )
        self.assertIn(
            "codex_subagent_or_internal_reviewer",
            rejections["codex_subagent_review"]["reasons"],
        )
        self.assertIn(
            "fallback_consensus_not_external_verdict",
            rejections["codex_fallback_consensus"]["reasons"],
        )

    def test_external_release_ready_verdict_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claude_valid_release_ready.md"
            path.write_text(
                "# Claude External Review\n\n"
                "Reviewer: Claude\n\n"
                "Verdict: `release_ready`\n\n"
                "Scope: Phoenix V3 aggregate 13-row / 9-capability release-readiness packet.\n",
                encoding="utf-8",
            )
            payload = intake.build_payload([path])

        self.assertEqual(payload["status"], "external_verdict_obtained")
        self.assertTrue(payload["valid_external_verdict_obtained"])
        self.assertTrue(payload["scoped_packet_authorized"])
        self.assertFalse(payload["release_authorized"])
        self.assertEqual(payload["accepted_verdict"], "release_ready")
        self.assertEqual(payload["status_line"], "external_verdict_obtained_claude_release_ready")
        self.assertEqual(payload["current_rejections"], [])

    def test_external_blocking_verdict_is_valid_but_not_release_authorization(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gemini_block_p1.md"
            path.write_text(
                "# Gemini External Review\n\n"
                "External reviewer: Gemini\n\n"
                "Verdict: block-p1\n\n"
                "Scope: Phoenix V3 aggregate 13-row / 9-capability release-readiness packet.\n",
                encoding="utf-8",
            )
            payload = intake.build_payload([path])

        self.assertEqual(payload["status"], "external_verdict_obtained")
        self.assertTrue(payload["valid_external_verdict_obtained"])
        self.assertFalse(payload["scoped_packet_authorized"])
        self.assertFalse(payload["release_authorized"])
        self.assertEqual(payload["accepted_verdict"], "block_p1")
        self.assertEqual(payload["status_line"], "external_verdict_obtained_gemini_block_p1")

    def test_current_core_gaps_claude_review_is_recorded_as_approve_blocked_not_release(self):
        classified = intake.classify_candidate(CORE_GAPS_REVIEW)
        self.assertTrue(classified["accepted"])
        self.assertEqual(classified["verdict"], "approve_blocked_not_release")
        self.assertEqual(classified["external_reviewer"], "claude")
        self.assertEqual(
            classified["status_line"],
            "external_verdict_obtained_claude_approve_blocked_not_release",
        )
        self.assertTrue(classified["external_reviewer_provenance"])
        self.assertFalse(classified["release_authorized"])
        self.assertFalse(classified["scoped_packet_authorized"])

        payload = intake.build_payload([CORE_GAPS_REVIEW])
        self.assertEqual(payload["status"], "external_verdict_obtained")
        self.assertTrue(payload["valid_external_verdict_obtained"])
        self.assertEqual(payload["accepted_verdict"], "approve_blocked_not_release")
        self.assertEqual(
            payload["status_line"],
            "external_verdict_obtained_claude_approve_blocked_not_release",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["scoped_packet_authorized"])

        saved = __import__("json").loads(CORE_GAPS_INTAKE.read_text(encoding="utf-8"))
        self.assertEqual(saved["accepted_verdict"], "approve_blocked_not_release")
        self.assertEqual(
            saved["status_line"],
            "external_verdict_obtained_claude_approve_blocked_not_release",
        )
        self.assertEqual(saved["accepted_candidates"][0]["path"], "docs\\reviews\\claude_phoenix_v3_external_review_2026-06-22.md")
        self.assertFalse(saved["release_authorized"])

    def test_current_core_gaps_status_stub_records_non_authorization(self):
        text = CORE_GAPS_STATUS.read_text(encoding="utf-8")
        for phrase in (
            "status_line: external_verdict_obtained_claude_approve_blocked_not_release",
            "verdict: approve_blocked_not_release",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "broad_v3_faster_than_v2_claim_authorized: false",
            "major_version_mandate_overridden: false",
            "proposal_only_not_authorization",
            "not an authorization",
            "## Goal-Level Decision Audit",
        ):
            self.assertIn(phrase, text)

    def test_set_a_set_b_proposal_is_recommendation_not_authorization(self):
        text = SET_A_SET_B_PROPOSAL.read_text(encoding="utf-8")
        for phrase in (
            "proposal only, not an authorization",
            "Set A",
            "Set B",
            "set_a_geomean_v3_vs_v2          >= 1.20x",
            "set_b_geomean_v3_vs_v2          >= 0.98x",
            "classification_frozen_before_run                  = true",
            "execution_path_executes (runtime_executed: True) on >= 2 set_A probes",
            "wins sourced from caches not the path",
            "does not alter the gate on its own",
        ):
            self.assertIn(phrase, text)

    def test_codex_fallback_with_release_ready_label_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "codex_fake_release_ready.md"
            path.write_text(
                "# Codex Subagent Review\n\n"
                "Reviewer: Codex subagent\n\n"
                "Verdict: release_ready\n\n"
                "This fallback consensus cannot substitute for a Claude/Gemini external release authorization.\n",
                encoding="utf-8",
            )
            payload = intake.build_payload([path])

        self.assertEqual(payload["status"], "missing_external_verdict")
        self.assertIsNone(payload["status_line"])
        self.assertFalse(payload["release_authorized"])
        rejection = payload["current_rejections"][0]
        self.assertIn("codex_subagent_or_internal_reviewer", rejection["reasons"])
        self.assertIn("cannot_substitute_for_external_authorization", rejection["reasons"])

    def test_external_verdict_template_and_request_are_intake_aligned(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        request = REVIEW_REQUEST.read_text(encoding="utf-8")
        for label in intake.VALID_VERDICT_LABELS:
            self.assertIn(f"`{label}`", template)
            self.assertIn(f"`{label}`", request)
        self.assertIn("Reviewer: Claude", template)
        self.assertIn("Verdict: `approve_blocked_not_release`", template)
        self.assertIn("scripts/v3_phoenix_external_verdict_intake.py", request)
        self.assertIn("phoenix_v3_external_verdict_response_template_2026-06-22.md", request)

        sample = (
            "# Claude External Review\n\n"
            "Reviewer: Claude\n"
            "Verdict: `block_p0`\n"
            "Scope: Phoenix V3 aggregate 13-row / 9-capability release-readiness packet.\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claude_template_style_verdict.md"
            path.write_text(sample, encoding="utf-8")
            payload = intake.build_payload([path])
        self.assertEqual(payload["status"], "external_verdict_obtained")
        self.assertFalse(payload["release_authorized"])
        self.assertEqual(payload["accepted_verdict"], "block_p0")


if __name__ == "__main__":
    unittest.main()
