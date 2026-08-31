from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3018_hausdorff_numba_no_host_sync_comparison_l4_pod_2026-06-01.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3018_hausdorff_numba_no_host_sync_comparison_l4_pod_2026-06-01.json"


class Goal3018HausdorffNumbaNoHostSyncComparisonL4PodTest(unittest.TestCase):
    def test_report_records_post_fast_path_result(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3018",
            "partner_numba_witness_exact",
            "partner_numba_block_nearest_exact",
            "0.7739660553634167",
            "1.0773870013654232",
            "dense device-score path is the current faster Numba Hausdorff path",
            "does not authorize v2.6 release",
        ):
            self.assertIn(phrase, text)

    def test_artifact_contract(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal3016")
        self.assertEqual(data["commit"], "4c9f947814662ebfc4575710f274b523f5617b58")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA L4, 565.57.01")
        self.assertTrue(data["all_match_oracle"])
        self.assertTrue(data["all_claim_flags_false"])
        self.assertGreater(data["block_vs_dense_wall_ratio"], 1.0)
        dense = next(row for row in data["evidence_summaries"] if row["mode"] == "partner_numba_witness_exact")
        block = next(row for row in data["evidence_summaries"] if row["mode"] == "partner_numba_block_nearest_exact")
        self.assertEqual(dense["score_operation"], "pairwise_l2_sq_score_rows_2d")
        self.assertEqual(block["score_operation"], "pairwise_l2_sq_block_nearest_rows_2d")
        self.assertEqual(dense["materialized_summary_row_count"], 4_194_304)
        self.assertEqual(block["materialized_summary_row_count"], 16_384)
        self.assertFalse(dense["host_score_row_materialization_used"])
        self.assertFalse(block["host_score_row_materialization_used"])
        self.assertFalse(dense["rt_core_accelerated"])
        self.assertFalse(block["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
