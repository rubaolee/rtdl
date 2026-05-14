from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2011_v2_0_progress_report_for_external_review_2026-05-14.md"


class Goal2011V20ProgressReportForExternalReviewTest(unittest.TestCase):
    def test_report_exists_and_names_recent_goal_chain(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for goal in ("Goal2000", "Goal2003", "Goal2006", "Goal2009"):
            self.assertIn(goal, text)
        self.assertIn("Python + RTDL + partner tensors", text)
        self.assertIn("generic_ray_primitive_candidate_witness_pairs", text)

    def test_report_keeps_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Not allowed yet", text)
        self.assertIn("final v2.0 release readiness", text)
        self.assertIn("broad RT-core speedup claims", text)
        self.assertIn("package-install claims", text)
        self.assertIn("arbitrary PyTorch/CuPy acceleration claims", text)

    def test_report_records_latest_pod_effects(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("0.002519239", text)
        self.assertIn("0.003932310", text)
        self.assertIn("2.46x", text)
        self.assertIn("strict priority-flag parity", text)
        self.assertIn("Claude Goal2010: `accept`", text)


if __name__ == "__main__":
    unittest.main()
