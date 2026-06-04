from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3229_rayjoin_public_count_coverage_summary_2026-06-03.md"
PIP = ROOT / "docs" / "reports" / "goal3227_rayjoin_public_pip_count_probe_2026-06-03.json"
LSI = ROOT / "docs" / "reports" / "goal3218_rayjoin_public_lsi_dense_count_probe_2026-06-03.json"
OVERLAY = ROOT / "docs" / "reports" / "goal3225_rayjoin_public_overlay_active_count_probe_2026-06-03.json"


class Goal3229RayJoinPublicCountCoverageSummaryTest(unittest.TestCase):
    def test_summary_covers_all_three_rayjoin_count_families(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "PIP: public positive-assignment count",
            "LSI: public segment-intersection count",
            "overlay_seed: public active pair-dependency count",
            "Goal3227",
            "Goal3218",
            "Goal3225",
            "pip_county512",
            "lsi_county256_soil256_count512",
            "overlay_county256_soil256",
        ):
            self.assertIn(phrase, report)

    def test_summary_matches_artifact_counts(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        pip = json.loads(PIP.read_text(encoding="utf-8"))
        lsi = json.loads(LSI.read_text(encoding="utf-8"))
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

        self.assertEqual(pip["rows"][0]["expected_positive_assignment_count"], 1430)
        self.assertIn("`1430`", report)

        lsi_counts = {
            row["case"]: row["validation"]["dense_intersection_count"]
            for row in lsi["rows"]
        }
        self.assertEqual(lsi_counts["lsi_county256_soil256_count48"], 34)
        self.assertEqual(lsi_counts["lsi_county256_soil256_count512"], 269)
        self.assertIn("`269`", report)

        overlay_counts = {
            row["case"]: row["expected_active_seed_count"]
            for row in overlay["rows"]
        }
        self.assertEqual(overlay_counts["overlay_county128_soil128"], 1)
        self.assertEqual(overlay_counts["overlay_county256_soil256"], 9)
        self.assertIn("`9`", report)

    def test_summary_preserves_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "does not authorize release",
            "public speedup",
            "broad RT-core",
            "true zero-copy",
            "RTDL beats RayJoin",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
