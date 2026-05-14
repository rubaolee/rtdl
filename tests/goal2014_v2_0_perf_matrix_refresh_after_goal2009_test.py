from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2014_v2_0_perf_matrix_refresh_after_goal2009_2026-05-14.md"


class Goal2014V20PerfMatrixRefreshAfterGoal2009Test(unittest.TestCase):
    def test_report_names_goal2009_as_current_road_hazard_row(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("The current best road-hazard row is therefore Goal2009", text)
        self.assertIn("road_hazard_prepared_cupy_cached_triangle_lookup_2048.json", text)
        self.assertIn("road_hazard_prepared_cupy_cached_triangle_lookup_4096.json", text)

    def test_report_records_current_speedups_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("1.38x", text)
        self.assertIn("2.46x", text)
        self.assertIn("Native OptiX remains a generic candidate-witness producer", text)
        self.assertIn("Not allowed", text)
        self.assertIn("v2.0 final release authorization", text)
        self.assertIn("arbitrary PyTorch/CuPy acceleration claims", text)

    def test_report_identifies_json_followup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("machine-readable JSON successor", text)
        self.assertIn("goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json", text)


if __name__ == "__main__":
    unittest.main()
