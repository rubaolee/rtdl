from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3005_v2_6_numba_partner_progress_after_rayjoin_2026-06-01.md"


class Goal3005V26NumbaPartnerProgressAfterRayjoinTest(unittest.TestCase):
    def test_report_summarizes_completed_numba_evidence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "v2.6 is now an internal development lane",
            "Users choose the partner",
            "Goal2995",
            "Goal3000",
            "Goal3003",
            "Goal3004",
            "segmented_count_i64",
            "segmented_sum_f64",
            "segmented_min_f64",
            "segmented_max_f64",
            "compact_mask_i64",
            "_numba_cuda_redirector",
            "accept-with-boundary",
        ):
            self.assertIn(phrase, text)

    def test_report_blocks_release_and_speedup_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "None of this authorizes",
            "v2.6 release",
            "public speedup wording",
            "Numba speedup wording",
            "RT-core speedup wording",
            "whole-app speedup wording",
            "true-zero-copy wording",
            "automatic partner selection",
            "app-specific native-engine logic",
            "RTDL beats RayJoin",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
