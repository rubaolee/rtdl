from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2818_rtnn_campaign_checkpoint_2026-05-31.md"
GOAL2817_DIR = ROOT / "docs" / "reports" / "goal2817_rtnn_block_partial_aggregate_pod"
GOAL2814_DIR = ROOT / "docs" / "reports" / "goal2814_rtnn_unsorted_topk_scale_sweep_pod"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2818RtnnCampaignCheckpointTest(unittest.TestCase):
    def test_report_names_checkpoint_and_keeps_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2818 RTNN v2.5 Campaign Checkpoint", report)
        self.assertIn("accept-with-boundary", report)
        self.assertIn("No public RTDL-beats-CuPy claim is authorized", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)
        self.assertIn("No v2.5 release claim is authorized", report)
        self.assertIn("No native app-specific engine customization is introduced", report)

    def test_report_captures_current_small_and_large_row_position(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("5 of 6 tested", report)
        self.assertIn("all 6 tested", report)
        self.assertIn("32K uniform", report)
        self.assertIn("0.920x", report)
        self.assertIn("65K uniform", report)
        self.assertIn("1.077x", report)
        self.assertIn("131072 | uniform", report)
        self.assertIn("262144 | shell", report)

    def test_small_row_artifacts_match_checkpoint_summary(self) -> None:
        wins = 0
        rows = []
        for name in (
            "rtnn_block_partial_median_f32_32768.json",
            "rtnn_block_partial_median_f32_65536.json",
        ):
            payload = _load(GOAL2817_DIR / name)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["source_dirty"], [])
            for row in payload["rows"]:
                self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                ratio = float(row["cupy_grid_over_rtdl_elapsed_ratio"])
                rows.append((payload["point_count"], row["distribution"], ratio))
                if ratio > 1.0:
                    wins += 1

        self.assertEqual(len(rows), 6)
        self.assertEqual(wins, 5)
        self.assertLess(dict(((p, d), r) for p, d, r in rows)[(32768, "uniform")], 1.0)
        self.assertGreater(dict(((p, d), r) for p, d, r in rows)[(65536, "uniform")], 1.0)

    def test_large_row_artifacts_all_beat_cupy_grid(self) -> None:
        ratios = []
        for name in (
            "rtnn_unsorted_topk_scale_131072.json",
            "rtnn_unsorted_topk_scale_262144.json",
        ):
            payload = _load(GOAL2814_DIR / name)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["source_dirty"], [])
            for row in payload["rows"]:
                self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                ratios.append(float(row["cupy_grid_over_rtdl_elapsed_ratio"]))

        self.assertEqual(len(ratios), 6)
        self.assertTrue(all(ratio > 1.0 for ratio in ratios))

    def test_next_step_is_generic_small_row_amortization(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Batched prepared aggregate calls", report)
        self.assertIn("CUDA graph capture", report)
        self.assertIn("Event-ordered aggregate chaining", report)
        self.assertNotIn("native RTNN ABI", report)


if __name__ == "__main__":
    unittest.main()
