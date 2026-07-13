from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5416_full_reproduction_blocker_priority_refresh.json"
)


class Goal5416FullReproductionPriorityRefreshTest(unittest.TestCase):
    def test_global_status_keeps_full_reproduction_open(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["matched"])
        status = payload["current_global_status"]
        self.assertTrue(status["bounded_same_input_value_reproduction_complete"])
        self.assertTrue(status["level_b_representative_scalar_evidence_strong"])
        self.assertFalse(status["full_xhd_paper_reproduction_complete"])
        self.assertFalse(status["exact_paper_dataset_provenance_complete"])
        self.assertFalse(status["performance_ratio_authorized"])
        self.assertTrue(status["explicit_lb_line_closed"])

    def test_priority_order_returns_to_dataset_and_figure5(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        priorities = payload["priority_order"]
        self.assertEqual("exact_input_provenance_and_dataset_acquisition", priorities[0]["name"])
        self.assertEqual("figure5_level_b_value_and_denominator_matrix", priorities[1]["name"])
        self.assertTrue(priorities[1]["pod_needed_now"])
        self.assertEqual("figure_status_closeout_refresh", priorities[2]["name"])
        self.assertEqual("generic_system_extraction_only_when_app_neutral", priorities[3]["name"])

    def test_figure_matrix_blocks_or_limits_every_figure(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        figures = payload["figure_matrix"]
        self.assertIn("full_matrix_not_reproduced", figures["figure5"]["status"])
        self.assertIn("lb_comparison_logs_missing", figures["figure7"]["status"])
        self.assertIn("tune_radius_logs_missing", figures["figure8"]["status"])
        self.assertIn("author_denominator_missing", figures["figure9"]["status"])
        self.assertIn("scalability_logs_missing", figures["figure10"]["status"])
        self.assertIn("denominator_not_aligned", figures["figure11"]["status"])
        for figure_name, figure in figures.items():
            self.assertIn("blocked_by", figure, figure_name)
            self.assertTrue(figure["blocked_by"], figure_name)

    def test_claim_boundary_forbids_full_or_ratio_claims(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["priority_refresh_claimed"])
        self.assertTrue(boundary["figure5_level_b_next_claimed"])
        for key in (
            "figure5_reproduction_claimed",
            "figure7_reproduction_claimed",
            "figure8_reproduction_claimed",
            "figure9_reproduction_claimed",
            "figure10_reproduction_claimed",
            "figure11_reproduction_claimed",
            "performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(boundary[key], key)

    def test_next_goal_requires_denominator_separation(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        next_goal = payload["recommended_next_goal"]
        self.assertEqual("Goal5417_figure5_level_b_same_pod_matrix_plan", next_goal["name"])
        for required in (
            "author Running.AvgTime",
            "author process wall",
            "RTDL route wall",
            "RTDL process wall",
            "cold vs warm process",
        ):
            self.assertIn(required, next_goal["must_keep_separate"])
        self.assertIn(
            "restart explicit -lb row identity probing without new author matrix or external review",
            payload["forbidden_next_work"],
        )


if __name__ == "__main__":
    unittest.main()
