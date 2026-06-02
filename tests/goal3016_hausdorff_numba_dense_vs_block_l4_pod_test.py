from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "goal3016_hausdorff_numba_mode_comparison_pod_runner.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3016_hausdorff_numba_dense_vs_block_l4_pod_2026-06-01.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3016_hausdorff_numba_dense_vs_block_l4_pod_2026-06-01.json"


class Goal3016HausdorffNumbaDenseVsBlockL4PodTest(unittest.TestCase):
    def test_runner_compares_both_modes(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for phrase in (
            "partner_numba_witness_exact",
            "partner_numba_block_nearest_exact",
            "block_vs_dense_wall_ratio",
            "all_claim_flags_false",
            "nvidia-smi",
        ):
            self.assertIn(phrase, source)

    def test_report_blocks_public_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Dense-vs-Block",
            "internal phase-timing evidence only",
            "does not authorize",
            "RT-core speedup wording",
            "block_vs_dense_wall_ratio",
        ):
            self.assertIn(phrase, text)

    def test_artifact_contract_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3016 pod artifact has not been collected yet")

        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal3016")
        self.assertEqual(data["source_dirty"], [])
        self.assertTrue(data["all_match_oracle"])
        self.assertTrue(data["all_claim_flags_false"])
        self.assertIsInstance(data["block_vs_dense_wall_ratio"], float)
        modes = {row["mode"] for row in data["evidence_summaries"]}
        self.assertEqual(modes, {"partner_numba_witness_exact", "partner_numba_block_nearest_exact"})
        dense = next(row for row in data["evidence_summaries"] if row["mode"] == "partner_numba_witness_exact")
        block = next(row for row in data["evidence_summaries"] if row["mode"] == "partner_numba_block_nearest_exact")
        self.assertEqual(dense["score_operation"], "pairwise_l2_sq_score_rows_2d")
        self.assertEqual(block["score_operation"], "pairwise_l2_sq_block_nearest_rows_2d")
        self.assertGreater(block["logical_pair_count"], block["materialized_summary_row_count"])


if __name__ == "__main__":
    unittest.main()
