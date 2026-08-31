from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3837_barnes_hut_numba_exact_force_refresh_2026-06-08.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3837_barnes_hut_numba_exact_force_refresh_a5000"
    / "summary.json"
)
MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"


class Goal3837BarnesHutNumbaExactForceRefreshTest(unittest.TestCase):
    def test_artifact_records_current_head_same_contract_evidence(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3762.barnes_hut_numba_block_reduce_force_probe.v1")
        self.assertEqual(payload["source_commit_short"], "576a5ba7")
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual(payload["body_counts"], [1024, 2048, 4096, 8192, 16384])
        self.assertEqual(payload["repeat"], 10)
        self.assertEqual(payload["warmup"], 3)
        self.assertTrue(payload["correctness"]["matches_oracle"])
        self.assertLess(payload["correctness"]["max_relative_error"], 1.0e-12)
        self.assertTrue(payload["summary"]["all_force_counts_match"])
        self.assertGreaterEqual(payload["summary"]["geomean_numba_speedup_vs_cupy"], 0.90)
        self.assertLess(payload["summary"]["geomean_numba_speedup_vs_cupy"], 1.0)
        for row in payload["rows"]:
            self.assertTrue(row["force_counts_match"])
            self.assertGreater(row["numba_speedup_vs_cupy"], 0.75)
            self.assertEqual(
                row["numba"]["metadata"]["numba_force_kernel_strategy"],
                "block_source_target_stride_512_reduce_fastmath_true",
            )
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["rt_core_speedup_claim_authorized"])

    def test_report_keeps_claim_boundary_and_tuning_conclusion_honest(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Barnes-Hut Numba Exact-Force Refresh", text)
        self.assertIn("not a native engine change", text)
        self.assertIn("0.914x", text)
        self.assertIn("512-thread block-reduction strategy remains the default", text)
        self.assertIn("CuPy remains the faster measured continuation", text)
        self.assertIn("does not authorize", text)
        self.assertIn("hierarchical Barnes-Hut acceleration claims", text)
        self.assertIn("RT-core speedup claims", text)

    def test_learner_matrix_cites_goal3837_without_overclaiming(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")
        self.assertIn("Goal3837 current-head no-RawKernel exact-force evidence", text)
        self.assertIn("CuPy remains the faster measured continuation", text)
        self.assertIn("no broad N-body acceleration claim", text)


if __name__ == "__main__":
    unittest.main()
