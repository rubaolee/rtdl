from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2814_rtnn_unsorted_topk_scale_sweep_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2814_rtnn_unsorted_topk_scale_sweep_pod"
ARTIFACT_131072 = ARTIFACT_DIR / "rtnn_unsorted_topk_scale_131072.json"
ARTIFACT_262144 = ARTIFACT_DIR / "rtnn_unsorted_topk_scale_262144.json"
EXPECTED_COMMIT = "8db92cafaf8b054dcaed67a40b9fa6ca31828066"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2814RtnnUnsortedTopKScaleSweepTest(unittest.TestCase):
    def test_scale_sweep_artifacts_are_clean_and_all_rows_beat_cupy_grid(self) -> None:
        ratios = []
        for artifact in (ARTIFACT_131072, ARTIFACT_262144):
            payload = _load(artifact)
            with self.subTest(artifact=artifact.name):
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["source_commit"], EXPECTED_COMMIT)
                self.assertEqual(payload["source_dirty"], [])
                self.assertIn("prepared_query_aggregate_float32_median", payload["harness_version"])
                self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
                self.assertFalse(payload["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])
                for row in payload["rows"]:
                    self.assertEqual(row["status"], "pass")
                    self.assertEqual(row["rtdl_elapsed_statistic"], "median")
                    self.assertEqual(row["cupy_grid_elapsed_statistic"], "median")
                    self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                    self.assertEqual(float(row["rtdl_phase_summary"]["upload_sec"]), 0.0)
                    ratio = float(row["cupy_grid_over_rtdl_elapsed_ratio"])
                    ratios.append(ratio)
                    self.assertGreater(ratio, 1.0)

        self.assertEqual(len(ratios), 6)
        self.assertGreater(min(ratios), 1.9)

    def test_report_explains_small_row_overhead_without_overclaiming(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        collapsed = " ".join(report.split())

        self.assertIn("accept-with-boundary", report)
        self.assertIn("RTDL is faster than the CuPy grid opponent in all 6 large-scale rows", collapsed)
        self.assertIn("small-row overhead", report)
        self.assertIn("No public RTDL-beats-CuPy claim is authorized before external review", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)


if __name__ == "__main__":
    unittest.main()
