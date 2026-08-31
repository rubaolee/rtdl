from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal3562_rtnn_alternating_same_scalar_probe_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3562_rtnn_alternating_same_scalar_probe_2026-06-06.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3560_claude_review_goal3556_3559_v29_perf_cleanup_2026-06-06.md"


class Goal3562RTNNAlternatingSameScalarProbeTest(unittest.TestCase):
    def test_rtnn_alternating_probe_closes_claude_required_item(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(payload["repeat"], 9000)
        self.assertEqual(len(payload["runs"]), 10)
        self.assertEqual(len(payload["values"]["v23"]), 5)
        self.assertEqual(len(payload["values"]["v28"]), 5)
        self.assertAlmostEqual(payload["v28_speedup_vs_v23"], 1.0109481139260648)
        self.assertGreater(payload["v28_speedup_vs_v23"], 1.0)
        self.assertLess(payload["v28_speedup_vs_v23"], 1.03)

    def test_artifacts_exist_for_each_trial(self) -> None:
        expected = {
            f"{lane}_trial{trial}.json"
            for lane in ("v23", "v28")
            for trial in range(1, 6)
        }
        actual = {path.name for path in SUMMARY.parent.glob("*.json")} - {"summary.json"}
        self.assertEqual(expected, actual)

    def test_report_and_review_line_up(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIn("Required before stable closeout: alternating RTNN probe", review)
        self.assertIn("This closes the required Goal3560 review item", report)
        self.assertIn("RTNN is near parity", report)
        self.assertIn("internal benchmark evidence only", report)


if __name__ == "__main__":
    unittest.main()
