from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REGISTRY = ROOT / "scripts" / "goal2626_benchmark_embree_optix_baseline.py"
OVERLAY = ROOT / "docs" / "patches" / "goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch"
SUMMARY = ROOT / "docs" / "reports" / "goal3556_rtnn_probe_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3556_rtnn_median_repeat_metric_hardening_2026-06-06.md"


class Goal3556RTNNMedianRepeatMetricHardeningTest(unittest.TestCase):
    def test_runner_emits_repeat_median_min_and_max(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("import statistics", text)
        self.assertIn("elapsed_median_sec = statistics.median(elapsed_runs)", text)
        self.assertGreaterEqual(text.count('"elapsed_median_sec"'), 2)
        self.assertGreaterEqual(text.count('"elapsed_min_sec"'), 2)
        self.assertGreaterEqual(text.count('"elapsed_max_sec"'), 2)
        self.assertIn('"elapsed_sec": elapsed_sec', text)

    def test_goal2626_rtnn_current_rows_use_median_metric(self) -> None:
        import sys

        sys.path.insert(0, str(ROOT))
        from scripts import goal2626_benchmark_embree_optix_baseline as runner

        cases = {
            case.case_id: case
            for case in runner.build_cases("quick", ROOT / "scratch" / "goal3556_test")
        }
        self.assertEqual(
            ("elapsed_median_sec",),
            cases["rtnn_embree_prepared_3d_ranked_summary"].primary_metric_path,
        )
        self.assertEqual(
            ("elapsed_median_sec",),
            cases["rtnn_optix_prepared_3d_ranked_summary"].primary_metric_path,
        )

    def test_v23_overlay_carries_the_same_median_scalar(self) -> None:
        text = OVERLAY.read_text(encoding="utf-8")
        self.assertIn("elapsed_median_sec = statistics.median(elapsed_runs)", text)
        self.assertIn('"elapsed_median_sec": elapsed_median_sec', text)
        self.assertIn('"elapsed_min_sec": min(elapsed_runs)', text)
        self.assertIn('"elapsed_max_sec": max(elapsed_runs)', text)
        self.assertGreaterEqual(text.count('primary_metric_path=("elapsed_median_sec",)'), 2)

    def test_a5000_probe_shows_median_metric_narrows_but_does_not_solve_gap(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        v23 = payload["v23"]
        v28 = payload["v28"]

        last_speedup = v23["last_elapsed_median"] / v28["last_elapsed_median"]
        median_speedup = v23["run_median_of_trials"] / v28["run_median_of_trials"]

        self.assertAlmostEqual(last_speedup, 0.9590888245208963)
        self.assertAlmostEqual(median_speedup, 0.9694553574662198)
        self.assertGreater(median_speedup, last_speedup)
        self.assertLess(median_speedup, 1.0)
        self.assertEqual(len(v23["last_elapsed_trials"]), 3)
        self.assertEqual(len(v28["last_elapsed_trials"]), 3)

    def test_report_keeps_claim_boundary_and_next_step_clear(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("measurement hardening step, not a performance win", text)
        self.assertIn("internal benchmark evidence only", text)
        self.assertIn("does not authorize", text)
        self.assertIn("Rebuild the v2.3 overlay worktree", text)


if __name__ == "__main__":
    unittest.main()
