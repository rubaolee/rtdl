from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2411_codex_counter_review_goal2409_cell_graph_safety_2026-05-19.md"


class Goal2411RtDbscanCellGraphSafetyCounterReviewTest(unittest.TestCase):
    def test_report_records_the_radius_cell_correctness_hole(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("supersedes the unsafe part", report)
        self.assertIn("two points inside the same cell can be farther apart", report)
        self.assertIn("sqrt(3) * radius", report)
        self.assertIn("same-cell disconnected-component case", report)

    def test_corrected_target_uses_clique_safe_microcells(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("clique-safe microcell graph", report)
        self.assertIn("microcell_size = radius / sqrt(3)", report)
        self.assertIn("neighbor_range = ceil(radius / microcell_size)", report)
        self.assertIn("radius_graph_components_3d_cupy_microcell_graph_partner_columns", report)
        self.assertIn("optix_rt_core_flags_cupy_microcell_graph_components_3d", report)

    def test_report_preserves_engine_boundary_and_abort_policy(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("no DBSCAN-native ABI", report)
        self.assertIn("Do not implement the unsafe radius-cell component graph", report)
        self.assertIn("correct but slower", report)
        self.assertIn("No release claim", report)


if __name__ == "__main__":
    unittest.main()
