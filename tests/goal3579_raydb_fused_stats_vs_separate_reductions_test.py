from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3579_raydb_fused_stats_vs_separate_reductions_2026-06-06.md"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "raydb_style" / "README.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3578_raydb_grouped_i64_mode_reprobe_current_a5000"


class Goal3579RaydbFusedStatsVsSeparateReductionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")
        cls.artifacts = {
            mode: json.loads((ARTIFACT_DIR / f"{mode}.json").read_text(encoding="utf-8"))
            for mode in ("count", "sum", "min", "max", "stats")
        }

    def test_report_records_primitive_choice_not_public_claim(self) -> None:
        self.assertIn("primitive-choice packet", self.report)
        self.assertIn("fused generic `stats` reduction", self.report)
        self.assertIn("not authorize public speedup claims", self.report)
        for boundary in (
            "whole-app acceleration claims",
            "broad RT-core speedup claims",
            "true zero-copy claims",
            "paper reproduction claims",
        ):
            self.assertIn(boundary, self.report)

    def test_fused_stats_is_materially_better_than_four_separate_reductions(self) -> None:
        separate = sum(
            self.artifacts[mode]["metadata"]["timings"]["query_median_sec"]
            for mode in ("count", "sum", "min", "max")
        )
        fused = self.artifacts["stats"]["metadata"]["timings"]["query_median_sec"]
        self.assertAlmostEqual(separate, 0.0018938756547868252)
        self.assertAlmostEqual(fused, 0.0005253716371953487)
        self.assertGreater(separate / fused, 3.5)
        self.assertIn("3.604830411x", self.report)

    def test_readme_recommends_stats_for_full_grouped_summary(self) -> None:
        self.assertIn("`--mode stats` instead of running four separate modes", self.readme)
        self.assertIn("returns all four fields", self.readme)
        self.assertIn("launch", self.readme)
        self.assertIn("single-output queries and diagnostic isolation", self.readme)


if __name__ == "__main__":
    unittest.main()
