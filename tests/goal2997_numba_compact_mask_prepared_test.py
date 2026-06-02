from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
NUMBA_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2997_numba_compact_mask_prepared_2026-06-01.md"
RUNNER = REPO_ROOT / "scripts" / "goal2997_numba_compact_mask_pod_runner.py"


class Goal2997NumbaCompactMaskPreparedTest(unittest.TestCase):
    def test_descriptor_is_generic_compact_mask(self) -> None:
        descriptor = rt.describe_numba_compact_mask_i64()
        self.assertEqual(descriptor["operation"], "compact_mask_i64")
        self.assertEqual(descriptor["partner"], "numba")
        self.assertEqual(descriptor["input_columns"], ("values:int64", "mask:bool"))
        self.assertEqual(descriptor["output_columns"], ("values:int64", "original_indices:int64"))
        self.assertTrue(descriptor["stable_input_order"])
        self.assertTrue(descriptor["host_prefix_sum_used"])
        self.assertFalse(descriptor["raw_kernel_required"])
        self.assertFalse(descriptor["replaces_rt_traversal"])
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_numba_compact_source_is_stable_order_not_app_specific(self) -> None:
        source = NUMBA_CONTINUATION.read_text(encoding="utf-8")
        for phrase in (
            "NUMBA_COMPACT_MASK_I64_OPERATION",
            "run_numba_compact_mask_i64",
            "run_numba_mask_indices_i64",
            "_numba_compact_count_blocks_i64_kernel",
            "_numba_compact_scatter_i64_kernel",
            "_numba_iota_i64_kernel",
            "stable_input_order",
            "host_prefix_sum_used",
        ):
            self.assertIn(phrase, source)
        self.assertNotIn("rayjoin", source.lower())
        self.assertNotIn("triangle_count", source.lower())

    def test_partner_mask_indices_accepts_numba_branch_and_rejects_host_mask(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")
        self.assertIn("run_numba_mask_indices_i64", source)
        self.assertIn("prepare_v2_6_neutral_partner_handoff", source)
        mask = np.asarray([False, True, False, True], dtype=np.bool_)
        with self.assertRaisesRegex(RuntimeError, "Numba neutral handoff rejected"):
            rt.partner_mask_indices(mask, partner="numba")

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "compact_mask_i64",
            "RayJoin-style",
            "triangle-counting-style",
            "stable-input-order preserving",
            "not yet a performance claim",
            "CUDA pod evidence is still required",
        ):
            self.assertIn(phrase, text)

    def test_runner_records_stable_order_and_claim_boundary(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for phrase in (
            "run_numba_compact_mask_i64",
            "partner_mask_indices",
            "stable_input_order",
            "host_prefix_sum_used",
            "values_match_cpu",
            "indices_match_cpu",
            '"numba_speedup_claim_authorized": False',
        ):
            self.assertIn(phrase, source)


if __name__ == "__main__":
    unittest.main()
