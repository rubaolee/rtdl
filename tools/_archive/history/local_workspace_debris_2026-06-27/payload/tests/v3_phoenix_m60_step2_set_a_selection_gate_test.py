import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "phoenix_v3_m60_step2_set_a_selection_spatial_topology_stream_2026-06-23.md"
)
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m60_step2_set_a_selection_spatial_topology_stream_2026-06-23.md"
)


class V3PhoenixM60Step2SetASelectionGateTest(unittest.TestCase):
    def test_m60_selects_spatial_topology_stream_not_app_tuning(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn(
            "m60_spatial_topology_stream_selected_pending_external_review_not_release",
            report,
        )
        self.assertIn("Spatial/RayJoin point-location topology stream", report)
        self.assertIn("generic topology-stream prepared-handle", report)
        self.assertIn("internal residency", report)
        self.assertIn("full-M3 phase", report)
        self.assertIn("not permission to tune a RayJoin app route", report)
        self.assertIn("device-resident internal route delta", report)
        self.assertIn("2.282x", report)

    def test_m60_candidate_triage_preserves_current_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("LibRTS/AABB", report)
        self.assertIn("Set-B yellow/open control limitation", report)
        self.assertIn("Barnes-Hut", report)
        self.assertIn("focused-fix-covered for planning", report)
        self.assertIn("Grouped reduction", report)
        self.assertIn("bounded Step-2 technical closure", report)
        self.assertIn("M53 later backfilled the open Claude review debt", report)
        self.assertIn("RTDBSCAN/component union", report)
        self.assertIn("positive component-union evidence", report)
        self.assertIn("Spatial/RayJoin topology stream", report)
        self.assertIn("selected", report)

    def test_m60_packet_preserves_no_pod_no_release(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark run", text)
            self.assertIn("no paid POD spend", text)
            self.assertIn("no focused POD spend", text)
            self.assertIn("no public speedup wording", text)
            self.assertIn("no broad V3-over-V2 claim", text)
            self.assertIn("no V4 work", text)
            self.assertIn("no embedding", text)
            self.assertIn("no C ABI", text)
            self.assertIn("no true-zero-copy claim", text)
            self.assertNotIn("release_ready", text)
            self.assertNotIn("POD authorized", text)

    def test_m60_review_packet_requests_narrow_verdicts(self) -> None:
        review = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        self.assertIn(
            "accept_m60_select_spatial_topology_stream_for_local_set_a_step2",
            review,
        )
        self.assertIn("request_m60_changes_before_selection", review)
        self.assertIn("reject_m60_selection_choose_different_set_a_family", review)
        self.assertIn("M61 may proceed as local no-POD", review)
        self.assertIn("run_point_location_topology_stream_prepared_session", review)
        self.assertIn("codex_claude_antigravity_phoenix_v3_m53_goal_completion_3ai_consensus", review)

    def test_m60_external_reviews_and_consensus_close_selection_only(self) -> None:
        claude = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m60_step2_set_a_selection_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m60_step2_set_a_selection_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity_followup = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m60_debt_followup_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m60_step2_set_a_selection_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")
        audit = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m60_goal_completion_audit_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for text in (claude, antigravity, consensus, audit):
            self.assertIn(
                "accept_m60_select_spatial_topology_stream_for_local_set_a_step2",
                text,
            )
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark", text)
            self.assertIn("no paid POD spend", text)
            self.assertIn("no true-zero-copy", text)
            self.assertNotIn("release_ready", text)

        self.assertIn("p1b_superseded_by_m53_no_m60_verdict_change", claude)
        self.assertIn("antigravity_m60_m53_amendment_accept_no_verdict_change", antigravity_followup)
        self.assertIn("internal_routing_delta_not_public_row", consensus)
        self.assertIn("m60_goal_complete_3ai_accept_spatial_topology_stream_selected", audit)


if __name__ == "__main__":
    unittest.main()
