from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt
from examples.benchmark_apps.hausdorff_xhd import rtdl_hausdorff_distance_app as hausdorff


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3015_numba_block_nearest_rows_for_hausdorff_2026-06-01.md"
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_distance_app.py"
NUMBA_SOURCE = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
ADAPTER_SOURCE = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"


class Goal3015NumbaBlockNearestRowsForHausdorffTest(unittest.TestCase):
    def test_descriptor_sources_and_app_mode_are_generic(self) -> None:
        descriptor = rt.describe_numba_pairwise_l2_sq_block_nearest_rows_2d()
        self.assertEqual(descriptor["operation"], "pairwise_l2_sq_block_nearest_rows_2d")
        self.assertEqual(descriptor["partner"], "numba")
        self.assertEqual(descriptor["score_semantics"], "per_source_tile_nearest_squared_l2_distance")
        self.assertTrue(descriptor["bounded_tile_summary_rows"])
        self.assertFalse(descriptor["host_score_row_materialization_used"])
        self.assertFalse(descriptor["replaces_rt_traversal"])

        combined = (
            NUMBA_SOURCE.read_text(encoding="utf-8")
            + ADAPTER_SOURCE.read_text(encoding="utf-8")
            + APP.read_text(encoding="utf-8")
        )
        for phrase in (
            "run_numba_pairwise_l2_sq_block_nearest_rows_2d",
            "_numba_pairwise_l2_sq_block_nearest_rows_2d_kernel",
            "pairwise_l2_sq_block_nearest_rows_2d_partner_columns",
            "partner_numba_block_nearest_exact",
            "bounded_tile_summary_rows",
        ):
            self.assertIn(phrase, combined)
        self.assertNotIn("hausdorff", NUMBA_SOURCE.read_text(encoding="utf-8").lower())

    def test_report_states_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "pairwise_l2_sq_block_nearest_rows_2d",
            "partner_numba_block_nearest_exact",
            "bounded_tile_summary_rows: True",
            "rt_core_accelerated: False",
            "does not authorize",
            "RT-core speedup wording",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_block_nearest_rows_execute_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable block-nearest validation")

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
        payload = rt.pairwise_l2_sq_block_nearest_rows_2d_partner_columns(
            source,
            target,
            partner="numba",
            block_size=64,
            return_metadata=True,
        )
        columns = payload["columns"]
        metadata = payload["metadata"]
        self.assertEqual(metadata["logical_pair_count"], 6)
        self.assertEqual(metadata["row_count"], 2)
        self.assertEqual(metadata["target_tile_count"], 1)
        self.assertTrue(metadata["bounded_tile_summary_rows"])
        self.assertEqual(columns["group_ids"].copy_to_host().tolist(), [0, 1])
        self.assertEqual(columns["item_ids"].copy_to_host().tolist(), [20, 21])
        self.assertEqual(columns["scores"].copy_to_host().tolist(), [1.0, 1.0])

    def test_hausdorff_block_nearest_mode_matches_oracle_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable Hausdorff Numba validation")

        payload = hausdorff.run_app("partner_numba_block_nearest_exact", copies=2)
        self.assertTrue(payload["matches_oracle"])
        self.assertFalse(payload["host_score_row_materialization_used"])
        self.assertTrue(payload["score_rows_generated_on_partner_device"])
        self.assertTrue(payload["bounded_tile_summary_rows"])
        self.assertEqual(
            payload["directed_a_to_b"]["v2_6_numba_score_row_operation"],
            "pairwise_l2_sq_block_nearest_rows_2d",
        )
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertFalse(payload["claim_boundary"]["numba_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
