from __future__ import annotations

import json
import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STANDARD = ROOT / "docs" / "reports" / "goal3583_rayjoin_hot_promoted_routes_a5000" / "summary.json"
STRESS = ROOT / "docs" / "reports" / "goal3583_rayjoin_hot_promoted_routes_stress_a5000" / "summary.json"
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3586_rayjoin_composite_score_from_hot_promoted_routes_2026-06-06.md"
)


def _composite(path: Path) -> tuple[float, float, float, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    ratios = data["ratios"]
    embree_total = sum(float(row["embree_sec"]) for row in ratios)
    optix_total = sum(float(row["optix_sec"]) for row in ratios)
    summed_speedup = embree_total / optix_total
    geo_mean = math.prod(float(row["optix_speedup_vs_embree"]) for row in ratios) ** (
        1.0 / len(ratios)
    )
    return embree_total, optix_total, summed_speedup, geo_mean


class Goal3586RayjoinCompositeScoreTest(unittest.TestCase):
    def test_standard_composite_score_matches_reported_values(self) -> None:
        embree_total, optix_total, summed_speedup, geo_mean = _composite(STANDARD)
        self.assertAlmostEqual(embree_total, 0.37346775364130735)
        self.assertAlmostEqual(optix_total, 0.002575232647359371)
        self.assertAlmostEqual(summed_speedup, 145.02291823003216)
        self.assertAlmostEqual(geo_mean, 85.95557643013733)

    def test_stress_composite_score_matches_reported_values(self) -> None:
        embree_total, optix_total, summed_speedup, geo_mean = _composite(STRESS)
        self.assertAlmostEqual(embree_total, 5.447204674594104)
        self.assertAlmostEqual(optix_total, 0.00719432532787323)
        self.assertAlmostEqual(summed_speedup, 757.152954077543)
        self.assertAlmostEqual(geo_mean, 159.83031849769964)

    def test_report_documents_score_definitions_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Primary app packet score: summed wall-time ratio", text)
        self.assertIn("Secondary route-balanced score: geometric mean", text)
        self.assertIn("145.023x", text)
        self.assertIn("757.153x", text)
        self.assertIn("full RayJoin paper reproduction", text)
        self.assertIn("full polygon overlay materialization", text)
        self.assertIn("true zero-copy claim", text)


if __name__ == "__main__":
    unittest.main()
