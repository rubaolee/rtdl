from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "app_adapters" / "barnes_hut.py"
SCRIPT = ROOT / "scripts" / "goal3762_barnes_hut_numba_block_reduce_force_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3762_barnes_hut_numba_block_reduce_force_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3762_barnes_hut_numba_block_reduce_force_a5000" / "summary.json"


class Goal3762BarnesHutTiledNumbaForceProbeTest(unittest.TestCase):
    def test_numba_kernel_uses_block_reduction_and_preserves_boundaries(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("cuda.shared.array(shape=512, dtype=float64)", text)
        self.assertIn("for j in range(lane, target_count, 512)", text)
        self.assertIn("partial_fx[lane] = fx", text)
        self.assertIn("stride = 256", text)
        self.assertIn("cuda.syncthreads()", text)
        self.assertIn("source_count >= 512 and target_count >= 512", text)
        self.assertIn("block_source_target_stride_512_reduce_fastmath_true", text)
        self.assertIn("global_target_stream_fastmath_true", text)
        self.assertNotIn("shared_target_tile_256_fastmath_true", text)
        self.assertIn('"raw_cuda_kernel_required": False', text)
        self.assertIn('"native_engine_row_contract": "not_called_partner_reference_only"', text)

    def test_probe_script_times_same_contract_partners(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("rtdl.goal3762.barnes_hut_numba_block_reduce_force_probe.v1", text)
        self.assertIn('partner="cupy"', text)
        self.assertIn('partner="numba"', text)
        self.assertIn("numba_speedup_vs_cupy", text)
        self.assertIn("hierarchical_barnes_hut_acceleration_claim_authorized", text)
        self.assertIn("public_speedup_claim_authorized", text)

    def test_report_and_artifact_when_present_are_claim_bounded(self) -> None:
        if not ARTIFACT.exists() or not REPORT.exists():
            self.skipTest("Goal3762 A5000 artifact/report not generated yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3762.barnes_hut_numba_block_reduce_force_probe.v1")
        self.assertTrue(payload["correctness"]["matches_oracle"])
        self.assertLess(payload["correctness"]["max_relative_error"], 1.0e-12)
        self.assertTrue(payload["summary"]["all_force_counts_match"])
        self.assertEqual(payload["body_counts"], [1024, 2048, 4096, 8192])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["hierarchical_barnes_hut_acceleration_claim_authorized"])
        for row in payload["rows"]:
            self.assertGreater(row["numba_speedup_vs_cupy"], 0.75)
            self.assertTrue(row["force_counts_match"])
            self.assertEqual(
                row["numba"]["metadata"]["numba_force_kernel_strategy"],
                "block_source_target_stride_512_reduce_fastmath_true",
            )
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Barnes-Hut Numba Block-Reduce Exact-Force Probe", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
