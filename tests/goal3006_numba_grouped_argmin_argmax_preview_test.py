from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
NUMBA_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3006_numba_grouped_argmin_argmax_preview_2026-06-01.md"


class Goal3006NumbaGroupedArgminArgmaxPreviewTest(unittest.TestCase):
    def test_descriptors_are_generic_preview_operations(self) -> None:
        argmin = rt.describe_numba_grouped_argmin_f64()
        argmax = rt.describe_numba_grouped_argmax_f64()

        self.assertEqual(argmin["operation"], "grouped_argmin_f64")
        self.assertEqual(argmax["operation"], "grouped_argmax_f64")
        for descriptor in (argmin, argmax):
            self.assertEqual(descriptor["partner"], "numba")
            self.assertEqual(descriptor["status"], "preview_not_promoted")
            self.assertEqual(
                descriptor["input_columns"],
                ("group_ids:int64", "item_ids:int64", "scores:float64"),
            )
            self.assertIn("missing_group_ids:int64", descriptor["output_columns"])
            self.assertTrue(descriptor["host_present_group_compaction_used"])
            self.assertFalse(descriptor["raw_kernel_required"])
            self.assertFalse(descriptor["replaces_rt_traversal"])
            self.assertFalse(descriptor["promoted_performance_path"])
        self.assertEqual(argmin["tie_break"], "lowest_score_then_lowest_item_id")
        self.assertEqual(argmax["tie_break"], "highest_score_then_lowest_item_id")

    def test_source_adds_numba_kernels_without_app_or_torch_carrier_terms(self) -> None:
        source = NUMBA_CONTINUATION.read_text(encoding="utf-8")

        for phrase in (
            "run_numba_grouped_argmin_f64",
            "run_numba_grouped_argmax_f64",
            "_numba_grouped_argmin_score_f64_kernel",
            "_numba_grouped_argmax_score_f64_kernel",
            "_numba_grouped_arg_item_i64_kernel",
            "cuda.atomic.min",
            "cuda.atomic.max",
            "lowest_score_then_lowest_item_id",
            "highest_score_then_lowest_item_id",
            "_numba_cuda_redirector",
        ):
            self.assertIn(phrase, source)
        for forbidden in ("hausdorff", "rtnn", "rayjoin", "dbscan", "torch_cuda_tensor_for_triton_launch"):
            self.assertNotIn(forbidden, source.lower())

    def test_public_partner_adapter_accepts_numba_branch(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        for phrase in (
            'partner == "numba"',
            "_numba_grouped_arg_reduce",
            "run_numba_grouped_argmin_f64",
            "run_numba_grouped_argmax_f64",
            "prepare_v2_6_neutral_partner_handoff",
            "grouped_argmin_f64_partner_columns",
            "grouped_argmax_f64_partner_columns",
        ):
            self.assertIn(phrase, source)

    def test_report_blocks_release_and_speedup_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RTNN, Hausdorff, and RMQ-style workloads",
            "No app vocabulary is added",
            "host-observed present-group compaction",
            "not a performance",
            "does not authorize",
            "v2.6 release",
            "Numba speedup wording",
            "true-zero-copy wording",
            "automatic partner selection",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_numba_grouped_arg_reducers_match_reference_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable grouped arg reducer validation")

        import numpy as np
        from numba import cuda

        group_ids = cuda.to_device(np.asarray([0, 0, 1, 1, 1], dtype=np.int64))
        item_ids = cuda.to_device(np.asarray([9, 8, 2, 1, 3], dtype=np.int64))
        scores = cuda.to_device(np.asarray([4.0, 4.0, 7.0, 5.0, 5.0], dtype=np.float64))

        argmin = rt.run_numba_grouped_argmin_f64(group_ids, item_ids, scores, group_count=3)
        self.assertEqual(argmin["outputs"]["group_ids"].copy_to_host().tolist(), [0, 1])
        self.assertEqual(argmin["outputs"]["item_ids"].copy_to_host().tolist(), [8, 1])
        self.assertEqual(argmin["outputs"]["scores"].copy_to_host().tolist(), [4.0, 5.0])
        self.assertEqual(argmin["outputs"]["missing_group_ids"].copy_to_host().tolist(), [2])
        self.assertEqual(argmin["tie_break"], "lowest_score_then_lowest_item_id")

        argmax = rt.grouped_argmax_f64_partner_columns(
            {"group_ids": group_ids, "item_ids": item_ids, "scores": scores},
            group_count=3,
            partner="numba",
            return_metadata=True,
        )
        self.assertEqual(argmax["columns"]["group_ids"].copy_to_host().tolist(), [0, 1])
        self.assertEqual(argmax["columns"]["item_ids"].copy_to_host().tolist(), [8, 2])
        self.assertEqual(argmax["columns"]["scores"].copy_to_host().tolist(), [4.0, 7.0])
        self.assertEqual(argmax["columns"]["missing_group_ids"].copy_to_host().tolist(), [2])
        self.assertEqual(argmax["metadata"]["partner"], "numba")
        self.assertFalse(argmax["metadata"]["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
