from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2346_v2_2_rtnn_nearest_neighbor_campaign_2026-05-18.md"
RESEARCH_INDEX = ROOT / "docs" / "research" / "README.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2347_gemini_review_goal2346_rtnn_v2_2_campaign_2026-05-18.md"


class Goal2346V22RtnnCampaignTest(unittest.TestCase):
    def test_report_pins_paper_code_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("PPoP", text)
        self.assertIn("https://arxiv.org/abs/2201.01366", text)
        self.assertIn("https://horizon-lab.org/pubs/ppopp22.pdf", text)
        self.assertIn("https://github.com/horizon-research/rtnn", text)
        self.assertIn("MIT license", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("no full RTNN reproduction claim", text)
        self.assertIn("no speedup claim yet", text)

    def test_report_uses_existing_rtdl_memory(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for name in (
            "v0_5_rtnn_gap_summary_2026-04-11.md",
            "goal265_v0_5_rtnn_dataset_registry_2026-04-12.md",
            "goal266_v0_5_rtnn_baseline_registry_2026-04-12.md",
            "goal267_v0_5_rtnn_reproduction_matrix_2026-04-12.md",
            "goal274_v0_5_bounded_fixed_radius_comparison_2026-04-12.md",
        ):
            self.assertIn(name, text)

    def test_runtime_gap_is_generic_not_app_shaped(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("prepared_bounded_neighbor_search_3d", text)
        self.assertIn("radius+`K` bounded result contract", text)
        self.assertIn("query partitioning and batching", text)
        self.assertIn("explicit, explainable execution policy", text)
        self.assertIn("partner-owned output columns", text)
        self.assertIn("These contracts remain app-agnostic", text)
        self.assertNotIn("native rtnn app entry", text.lower())

    def test_external_review_and_risks_are_recorded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        review = GEMINI_REVIEW.read_text(encoding="utf-8")
        self.assertIn("Goal2347 Gemini review", text)
        self.assertIn("accept-with-boundary", review)
        for phrase in (
            "RTNN dependency drift",
            "Pod performance variability",
            "Real dataset preparation",
            "Harness integration complexity",
            "Non-uniform scalability",
        ):
            self.assertIn(phrase, text)

    def test_research_index_links_campaign(self) -> None:
        text = RESEARCH_INDEX.read_text(encoding="utf-8")
        self.assertIn("RTNN Nearest-Neighbor Campaign", text)
        self.assertIn("goal2346_v2_2_rtnn_nearest_neighbor_campaign_2026-05-18.md", text)


if __name__ == "__main__":
    unittest.main()
