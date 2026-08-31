from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3559_raydb_sum_count_probe_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3559_raydb_sum_count_stability_probe_2026-06-06.md"


class Goal3559RayDBSumCountStabilityProbeTest(unittest.TestCase):
    def test_probe_records_three_alternating_trials_per_mode_and_lane(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(payload["repeat"], 20000)
        self.assertEqual(payload["copies"], 120000)
        self.assertEqual(len(payload["runs"]), 12)

        for mode in ("count", "sum"):
            values = payload["by_mode"][mode]["values"]
            self.assertEqual(set(values), {"v23", "v28"})
            self.assertEqual(len(values["v23"]), 3)
            self.assertEqual(len(values["v28"]), 3)

    def test_raydb_gap_deescalates_to_near_parity(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        count = payload["by_mode"]["count"]
        total_sum = payload["by_mode"]["sum"]

        self.assertAlmostEqual(count["v28_speedup_vs_v23"], 0.9971188961785764)
        self.assertAlmostEqual(total_sum["v28_speedup_vs_v23"], 0.9870547477190499)
        self.assertGreater(count["v28_speedup_vs_v23"], 0.99)
        self.assertGreater(total_sum["v28_speedup_vs_v23"], 0.98)
        self.assertLess(total_sum["v28_speedup_vs_v23"], 1.0)

    def test_raw_artifacts_are_present_for_each_run(self) -> None:
        expected = {
            f"{lane}_{mode}_trial{trial}.json"
            for lane in ("v23", "v28")
            for mode in ("count", "sum")
            for trial in (1, 2, 3)
        }
        actual = {path.name for path in ARTIFACT_DIR.glob("*.json")} - {"summary.json"}
        self.assertEqual(expected, actual)

    def test_report_blocks_unnecessary_code_change(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not stable regressions", text)
        self.assertIn("one-run weak observation", text)
        self.assertIn("internal benchmark evidence only", text)
        self.assertIn("Do not change RayDB code solely", text)


if __name__ == "__main__":
    unittest.main()
