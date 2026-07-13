from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULTS_README = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "README.md"
REGISTER = ROOT / "history" / "internal_docs" / "xhd_review_opinions_register_2026-07-07.md"
STATUS = ROOT / "history" / "internal_docs" / "xhd_current_status_after_goal5314_2026-07-09.md"


class Goal5315XhdWaterBgStatusDocsTest(unittest.TestCase):
    def test_results_readme_records_corrected_denominator_and_boundaries(self) -> None:
        text = RESULTS_README.read_text(encoding="utf-8")

        self.assertIn("Full-Public WaterBodies -> BlockGroups Corrected Comparison", text)
        self.assertIn("n_points_cell=15", text)
        self.assertIn("n_points_cell = 8", text)
        self.assertIn("0.8970130085945129", text)
        self.assertIn("0.8964367508888245", text)
        self.assertIn("0.8964380566690101", text)
        self.assertIn("1.305780185645311e-06", text)
        self.assertIn("declared tolerance                = 2e-6", text)

        self.assertIn("exact paper WKT files recovered = not claimed", text)
        self.assertIn("Figure 5 fully reproduced = not claimed", text)
        self.assertIn("performance parity = not claimed", text)
        self.assertIn("author/RTDL identical internal precision = not claimed", text)

    def test_register_tracks_goal5313_and_goal5314_as_review_pending(self) -> None:
        text = REGISTER.read_text(encoding="utf-8")
        compact = " ".join(text.split())
        compact_lower = compact.lower()

        self.assertIn("## Goal5313 - X-HD WaterBodies/BG Author Config Alignment", text)
        self.assertIn("## Goal5314 - X-HD WaterBodies/BG Corrected Comparison Summary", text)
        self.assertIn("implemented_review_pending", text)
        self.assertIn("paper-branch logs use n_points_cell=8", compact_lower)
        self.assertIn("goal5311 remains config-sensitivity evidence", compact_lower)
        self.assertIn("1.305780185645311e-06", text)
        self.assertIn("approve_goal5314_xhd_water_bg_corrected_comparison_summary", text)

    def test_current_status_after_goal5314_is_bounded_and_actionable(self) -> None:
        text = STATUS.read_text(encoding="utf-8")

        self.assertIn("The active objective remains full X-HD paper reproduction", text)
        self.assertIn("This objective is **not yet complete**", text)
        self.assertIn("Goal5313: implemented / review pending", text)
        self.assertIn("Goal5314: implemented / review pending", text)
        self.assertIn("n_points_cell = 8", text)
        self.assertIn("n_points_cell = 15", text)
        self.assertIn("declared scalar tolerance = 2e-6", text)
        self.assertIn("Goal5316", text)

        self.assertIn("exact paper WKT files recovered by hash", text)
        self.assertIn("Figure 5 fully reproduced", text)
        self.assertIn("RTDL/native performance parity", text)
        self.assertIn("identical author/RTDL internal numeric precision", text)


if __name__ == "__main__":
    unittest.main()
