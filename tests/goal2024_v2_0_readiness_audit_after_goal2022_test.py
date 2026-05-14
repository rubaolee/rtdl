from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2024_v2_0_readiness_audit_after_goal2022_2026-05-14.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal2024_v2_0_readiness_audit_after_goal2022_2026-05-14.json"
MATRIX = ROOT / "docs" / "reports" / "goal2015_current_all_app_v18_v2_perf_analysis_after_goal2009_2026-05-14.json"
GOAL2023_REVIEW = ROOT / "docs" / "reviews" / "goal2023_external_review_goal2022_graph_compressed_metric_pattern_2026-05-14.md"


class Goal2024V20ReadinessAuditAfterGoal2022Test(unittest.TestCase):
    def test_audit_positions_v2_as_release_candidate_preparation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("release-candidate preparation lane", text)
        self.assertIn("not release authorization", text)
        self.assertIn("v2.0 is close, but not released", text)
        self.assertIn("final 3-AI release consensus", text)
        self.assertIn("explicit user release action", text)

    def test_audit_names_recent_weak_spot_closures_and_reviews(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2020", text)
        self.assertIn("Goal2021: `accept`", text)
        self.assertIn("Goal2022", text)
        self.assertIn("Goal2023: `accept-with-boundary`", text)
        self.assertIn("0.214x", text)
        self.assertIn("0.201x", text)
        self.assertIn("0.000007x", text)

    def test_audit_keeps_forbidden_claims_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Do not say v2.0 is released",
            "Do not say every app has a final whole-app speedup claim",
            "Do not say RT cores broadly accelerate every workload",
            "Do not claim true package installation support",
            "bounded rows into broad domain claims",
        ):
            self.assertIn(phrase, text)

    def test_json_matches_current_matrix_and_keeps_release_false(self) -> None:
        audit = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
        matrix = json.loads(MATRIX.read_text(encoding="utf-8-sig"))

        self.assertEqual(audit["verdict"], "accept-with-boundary")
        self.assertFalse(audit["release_authorized"])
        self.assertEqual(audit["matrix_row_count"], matrix["row_count"])
        self.assertEqual(audit["classification_counts"], matrix["classification_counts"])
        self.assertFalse(matrix["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(matrix["claim_boundary"]["whole_app_speedup_claim_authorized"])

    def test_goal2023_review_is_present_for_goal2022_boundary(self) -> None:
        text = GOAL2023_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Verdict: accept-with-boundary", text)
        self.assertIn("generic compressed metric-table continuation contract", text)
        self.assertIn("not broad graph traversal acceleration", text)


if __name__ == "__main__":
    unittest.main()
