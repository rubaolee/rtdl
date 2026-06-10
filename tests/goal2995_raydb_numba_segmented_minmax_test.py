from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

import rtdsl as rt
from examples.current.research_benchmarks.raydb_style import (
    rtdl_raydb_style_benchmark_app as raydb,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
NUMBA_CONTINUATION = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
RUNNER = REPO_ROOT / "scripts" / "goal2995_raydb_numba_minmax_pod_runner.py"
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2995_raydb_numba_segmented_minmax_prepared_2026-06-01.md"
)


class Goal2995RaydbNumbaSegmentedMinmaxTest(unittest.TestCase):
    def test_numba_minmax_descriptors_are_generic_grouped_reductions(self) -> None:
        min_descriptor = rt.describe_numba_segmented_min_f64()
        max_descriptor = rt.describe_numba_segmented_max_f64()
        self.assertEqual(min_descriptor["operation"], "segmented_min_f64")
        self.assertEqual(max_descriptor["operation"], "segmented_max_f64")
        for descriptor in (min_descriptor, max_descriptor):
            self.assertEqual(descriptor["partner"], "numba")
            self.assertEqual(descriptor["input_columns"], ("group_ids:int64", "values:float64"))
            self.assertEqual(descriptor["empty_group_fill"], "initial")
            self.assertFalse(descriptor["raw_kernel_required"])
            self.assertFalse(descriptor["replaces_rt_traversal"])
            self.assertFalse(descriptor["promoted_performance_path"])

    def test_numba_continuation_implements_minmax_without_raydb_terms(self) -> None:
        source = NUMBA_CONTINUATION.read_text(encoding="utf-8")
        for phrase in (
            "NUMBA_SEGMENTED_MIN_F64_OPERATION",
            "NUMBA_SEGMENTED_MAX_F64_OPERATION",
            "run_numba_segmented_min_f64",
            "run_numba_segmented_max_f64",
            "_numba_segmented_min_f64_kernel",
            "_numba_segmented_max_f64_kernel",
            "cuda.atomic.min",
            "cuda.atomic.max",
        ):
            self.assertIn(phrase, source)
        self.assertNotIn("raydb", source.lower())

    def test_partner_minmax_front_doors_accept_numba_branch_and_reject_host_columns(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")
        self.assertIn("run_numba_segmented_min_f64", source)
        self.assertIn("run_numba_segmented_max_f64", source)
        self.assertIn("prepare_v2_6_neutral_partner_handoff", source)
        group_ids = np.asarray([0, 1, 0], dtype=np.int64)
        values = np.asarray([1.0, 2.0, 3.0], dtype=np.float64)
        with self.assertRaisesRegex(RuntimeError, "Numba neutral handoff rejected"):
            rt.partner_group_min_by_key(group_ids, values, 2, partner="numba", initial=np.inf)
        with self.assertRaisesRegex(RuntimeError, "Numba neutral handoff rejected"):
            rt.partner_group_max_by_key(group_ids, values, 2, partner="numba", initial=-np.inf)

    def test_raydb_v2_6_numba_descriptor_supports_all_scalar_modes(self) -> None:
        expected = {
            "count": ("segmented_count_i64",),
            "sum": ("segmented_sum_f64",),
            "min": ("segmented_min_f64",),
            "max": ("segmented_max_f64",),
            "avg_as_sum_count": ("segmented_sum_f64", "segmented_count_i64"),
        }
        for mode, operations in expected.items():
            with self.subTest(mode=mode):
                descriptor = raydb.describe_raydb_v2_6_numba_neutral_continuation(mode)
                self.assertEqual(descriptor["selected_partner"], "numba")
                self.assertEqual(descriptor["status"], "executable_for_count_sum_min_max")
                self.assertEqual(descriptor["operations"], operations)
                self.assertIsNone(descriptor["blocked_reason"])
                self.assertTrue(descriptor["uses_v2_6_neutral_partner_handoff"])
                self.assertFalse(descriptor["uses_legacy_torch_carrier"])
                self.assertFalse(descriptor["uses_torch_conversion"])
                self.assertFalse(descriptor["replaces_rt_traversal"])

    def test_runner_and_report_record_pod_boundary(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        for phrase in (
            'MODES = ("count", "sum", "min", "max", "avg_as_sum_count")',
            "expected_mins",
            "expected_maxes",
            "dense_mins",
            "dense_maxes",
            "NUMBA_CUDA_USE_NVIDIA_BINDING",
            '"raydb_paper_reproduction_claim_authorized": False',
        ):
            self.assertIn(phrase, runner)
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "segmented_min_f64",
            "segmented_max_f64",
            "all five scalar aggregate modes",
            "Host NumPy arrays are rejected before CUDA execution",
            "CUDA pod evidence is still required",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
