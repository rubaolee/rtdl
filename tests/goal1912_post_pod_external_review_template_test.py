from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "handoff" / "GOAL1912_POST_POD_EXTERNAL_REVIEW_TEMPLATE_2026-05-13.md"
REPORT = ROOT / "docs" / "reports" / "goal1912_post_pod_external_review_template_2026-05-13.md"


class Goal1912PostPodExternalReviewTemplateTest(unittest.TestCase):
    def test_handoff_names_required_pod_artifacts_and_questions(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        for artifact in (
            "goal1903_fixed_radius_batch_pod.json",
            "goal1903_segment_polygon_batch_pod_512.json",
            "goal1903_segment_polygon_batch_pod_2048.json",
            "goal1889_road_hazard_prepared_reuse_pod_512.json",
            "goal1889_road_hazard_prepared_reuse_pod_2048.json",
            "goal1903_v2_partner_pod_batch_summary.json",
            "goal1905_v2_partner_pod_batch_acceptance.json",
        ):
            self.assertIn(artifact, text)
        self.assertIn("RTX-class GPU", text)
        self.assertIn("Goal1905 pass strictly", text)
        self.assertIn("Which exact primitive/backend/partner/app-row claims", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("Do not edit any file except the requested review file", text)

    def test_handoff_has_distinct_claude_and_gemini_output_paths(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("goal1912_claude_review_goal1903_post_pod_artifacts_2026-05-13.md", text)
        self.assertIn("goal1912_gemini_review_goal1903_post_pod_artifacts_2026-05-13.md", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("needs-more-evidence", text)

    def test_report_keeps_template_waiting_for_pod(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: template-ready-waiting-for-pod", text)
        self.assertIn("does not claim pod evidence exists", text)
        self.assertIn("does not authorize v2.0 release", text)
        self.assertIn("Run Goal1903 on an RTX pod", text)
        self.assertIn("Run Goal1905 strict acceptance", text)


if __name__ == "__main__":
    unittest.main()
