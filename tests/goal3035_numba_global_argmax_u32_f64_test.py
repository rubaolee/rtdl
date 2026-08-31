from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
NUMBA_SOURCE = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REDUCTIONS = REPO_ROOT / "src" / "rtdsl" / "adapters" / "reductions.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3035_numba_global_argmax_u32_f64_device_consumer_2026-06-02.md"


class Goal3035NumbaGlobalArgmaxU32F64Test(unittest.TestCase):
    def test_descriptor_and_public_exports_are_generic(self) -> None:
        descriptor = rt.describe_numba_global_argmax_u32_f64()

        self.assertEqual(descriptor["operation"], "global_argmax_u32_f64")
        self.assertEqual(descriptor["input_columns"], ("item_ids:uint32", "scores:float64"))
        self.assertEqual(descriptor["output_columns"], ("item_ids:uint32", "scores:float64", "row_indices:int64"))
        self.assertEqual(descriptor["tie_break"], "highest_score_then_lowest_item_id_then_lowest_row_index")
        self.assertEqual(descriptor["invalid_item_id_default"], 0xFFFFFFFF)
        self.assertFalse(descriptor["raw_kernel_required"])
        self.assertFalse(descriptor["replaces_rt_traversal"])
        self.assertFalse(descriptor["promoted_performance_path"])

        for name in (
            "NUMBA_GLOBAL_ARGMAX_U32_F64_OPERATION",
            "describe_numba_global_argmax_u32_f64",
            "run_numba_global_argmax_u32_f64",
            "global_argmax_u32_f64_partner_columns",
        ):
            self.assertIn(name, rt.__all__)

    def test_source_adds_device_consumer_without_app_terms_or_torch_carrier(self) -> None:
        numba_source = NUMBA_SOURCE.read_text(encoding="utf-8")
        adapter_source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        reductions_source = REDUCTIONS.read_text(encoding="utf-8")

        for phrase in (
            "NUMBA_GLOBAL_ARGMAX_U32_F64_OPERATION",
            "run_numba_global_argmax_u32_f64",
            "_numba_global_argmax_initial_block_reduce_u32_f64_kernel",
            "_numba_global_argmax_block_reduce_u32_f64_kernel",
            "multi_stage_block_reduce_no_global_atomics",
            "_as_numba_cuda_vector",
        ):
            self.assertIn(phrase, numba_source)
        for phrase in (
            "global_argmax_u32_f64_partner_columns",
            "prepare_v2_6_neutral_partner_handoff",
            "validate_v2_6_neutral_partner_handoff",
            "direct_device_handoff_authorized",
            "true_zero_copy_claim_authorized",
        ):
            self.assertIn(phrase, adapter_source)
        self.assertIn("global_argmax_u32_f64_partner_columns", reductions_source)

        numba_start = numba_source.index("def run_numba_global_argmax_u32_f64")
        numba_body = numba_source[numba_start : numba_source.index("def run_numba_pairwise_l2_sq_score_rows_2d", numba_start)]
        adapter_start = adapter_source.index("def global_argmax_u32_f64_partner_columns")
        adapter_body = adapter_source[adapter_start : adapter_source.index("def _torch_grouped_topk", adapter_start)]
        combined = (numba_body + "\n" + adapter_body).lower()
        for forbidden in (
            "hausdorff",
            "x-hd",
            "rayjoin",
            "rtnn",
            "dbscan",
            "torch_cuda_tensor_for_triton_launch",
        ):
            self.assertNotIn(forbidden, combined)

    def test_report_keeps_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3035",
            "global_argmax_u32_f64",
            "highest `float64` score",
            "lowest `uint32` item id",
            "0xffffffff",
            "does not authorize",
            "true-zero-copy wording",
            "app-specific native-engine behavior",
        ):
            self.assertIn(phrase, text)

    def test_numba_global_argmax_matches_reference_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable global argmax validation")

        import numpy as np
        from numba import cuda

        item_ids = cuda.to_device(np.asarray([9, 3, 7, 2, 0xFFFFFFFF, 5], dtype=np.uint32))
        scores = cuda.to_device(np.asarray([1.0, 4.0, 4.0, 4.0, 99.0, float("nan")], dtype=np.float64))

        result = rt.global_argmax_u32_f64_partner_columns(
            {"item_ids": item_ids, "scores": scores},
            partner="numba",
            return_metadata=True,
        )

        self.assertEqual(result["columns"]["item_ids"].copy_to_host().tolist(), [2])
        self.assertEqual(result["columns"]["row_indices"].copy_to_host().tolist(), [3])
        self.assertEqual(result["columns"]["scores"].copy_to_host().tolist(), [4.0])
        self.assertEqual(result["metadata"]["partner"], "numba")
        self.assertEqual(result["metadata"]["operation"], "global_argmax_u32_f64")
        self.assertEqual(result["metadata"]["reduction_strategy"], "multi_stage_block_reduce_no_global_atomics")
        self.assertFalse(result["metadata"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(result["metadata"]["true_zero_copy_claim_authorized"])

    def test_cupy_columns_cross_neutral_handoff_when_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable CuPy-to-Numba validation")

        try:
            import cupy
        except ImportError:
            self.skipTest("CuPy is required for cross-partner handoff validation")

        item_ids = cupy.asarray([6, 4, 5, 0xFFFFFFFF], dtype=cupy.uint32)
        scores = cupy.asarray([2.0, 8.0, 8.0, 100.0], dtype=cupy.float64)

        result = rt.global_argmax_u32_f64_partner_columns(
            {"item_ids": item_ids, "scores": scores},
            partner="numba",
            return_metadata=True,
        )

        self.assertEqual(result["columns"]["item_ids"].copy_to_host().tolist(), [4])
        self.assertEqual(result["columns"]["row_indices"].copy_to_host().tolist(), [1])
        self.assertEqual(result["metadata"]["neutral_handoff_status"], "accept")
        self.assertEqual(result["metadata"]["neutral_handoff_source_protocols"], ("cupy", "cupy"))
        self.assertTrue(result["metadata"]["direct_device_handoff_authorized"])
        self.assertFalse(result["metadata"]["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
