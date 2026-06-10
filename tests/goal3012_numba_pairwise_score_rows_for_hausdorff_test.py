from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt
from examples.current.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_distance_app as hausdorff


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3012_numba_pairwise_score_rows_for_hausdorff_2026-06-01.md"
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_distance_app.py"
NUMBA_SOURCE = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
ADAPTER_SOURCE = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"


class Goal3012NumbaPairwiseScoreRowsForHausdorffTest(unittest.TestCase):
    def test_descriptor_and_sources_are_generic(self) -> None:
        descriptor = rt.describe_numba_pairwise_l2_sq_score_rows_2d()
        self.assertEqual(descriptor["operation"], "pairwise_l2_sq_score_rows_2d")
        self.assertEqual(descriptor["partner"], "numba")
        self.assertEqual(descriptor["score_semantics"], "squared_l2_distance")
        self.assertFalse(descriptor["host_score_row_materialization_used"])
        self.assertFalse(descriptor["replaces_rt_traversal"])

        numba_source = NUMBA_SOURCE.read_text(encoding="utf-8")
        adapter_source = ADAPTER_SOURCE.read_text(encoding="utf-8")
        app_source = APP.read_text(encoding="utf-8")
        for phrase in (
            "run_numba_pairwise_l2_sq_score_rows_2d",
            "_numba_pairwise_l2_sq_score_rows_2d_kernel",
            "pairwise_l2_sq_score_rows_2d_partner_columns",
            "score_rows_generated_on_partner_device",
        ):
            self.assertIn(phrase, numba_source + adapter_source + app_source)
        self.assertNotIn("hausdorff", numba_source.lower())

    def test_report_states_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "pairwise_l2_sq_score_rows_2d",
            "host_score_row_materialization_used: False",
            "score_rows_generated_on_partner_device: True",
            "rt_core_accelerated: False",
            "does not authorize",
            "RT-core speedup wording",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_pairwise_score_rows_execute_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable pairwise score-row validation")

        import numpy as np

        try:
            import _numba_cuda_redirector  # noqa: F401
        except ImportError:
            pass
        from numba import cuda

        source = {
            "ids": cuda.to_device(np.asarray([10, 11], dtype=np.int64)),
            "x": cuda.to_device(np.asarray([0.0, 2.0], dtype=np.float64)),
            "y": cuda.to_device(np.asarray([0.0, 0.0], dtype=np.float64)),
        }
        target = {
            "ids": cuda.to_device(np.asarray([20, 21, 22], dtype=np.int64)),
            "x": cuda.to_device(np.asarray([0.0, 1.0, 3.0], dtype=np.float64)),
            "y": cuda.to_device(np.asarray([1.0, 0.0, 0.0], dtype=np.float64)),
        }
        payload = rt.pairwise_l2_sq_score_rows_2d_partner_columns(
            source,
            target,
            partner="numba",
            return_metadata=True,
        )
        columns = payload["columns"]
        metadata = payload["metadata"]
        self.assertEqual(metadata["row_count"], 6)
        self.assertFalse(metadata["host_score_row_materialization_used"])
        self.assertTrue(metadata["score_rows_generated_on_partner_device"])
        self.assertEqual(columns["group_ids"].copy_to_host().tolist(), [0, 0, 0, 1, 1, 1])
        self.assertEqual(columns["item_ids"].copy_to_host().tolist(), [20, 21, 22, 20, 21, 22])
        self.assertEqual(columns["scores"].copy_to_host().tolist(), [1.0, 1.0, 9.0, 5.0, 1.0, 1.0])

    def test_hausdorff_numba_mode_uses_device_score_rows_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable Hausdorff Numba validation")

        payload = hausdorff.run_app("partner_numba_witness_exact", copies=2)
        self.assertTrue(payload["matches_oracle"])
        self.assertFalse(payload["host_score_row_materialization_used"])
        self.assertTrue(payload["score_rows_generated_on_partner_device"])
        self.assertEqual(payload["directed_a_to_b"]["v2_6_numba_score_row_operation"], "pairwise_l2_sq_score_rows_2d")
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertFalse(payload["claim_boundary"]["numba_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
