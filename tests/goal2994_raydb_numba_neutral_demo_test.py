from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import (
    rtdl_raydb_style_benchmark_app as raydb,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "goal2994_raydb_numba_neutral_demo_pod_runner.py"
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2994_raydb_numba_neutral_demo_prepared_2026-06-01.md"
)
ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"


class Goal2994RaydbNumbaNeutralDemoTest(unittest.TestCase):
    def test_generic_front_doors_accept_numba_branch(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")
        self.assertIn('if partner == "numba":', source)
        self.assertIn("prepare_v2_6_neutral_partner_handoff", source)
        self.assertIn("validate_v2_6_neutral_partner_handoff", source)
        self.assertIn("run_numba_segmented_count_i64", source)
        self.assertIn("run_numba_segmented_sum_f64", source)
        self.assertIn("run_numba_segmented_min_f64", source)
        self.assertIn("run_numba_segmented_max_f64", source)
        self.assertIn("partner must be 'triton', 'torch', 'cupy', or 'numba'", source)

    def test_numba_front_door_rejects_host_columns_before_cuda_execution(self) -> None:
        group_ids = np.asarray([0, 1, 0], dtype=np.int64)
        values = np.asarray([1.0, 2.0, 3.0], dtype=np.float64)
        with self.assertRaisesRegex(RuntimeError, "Numba neutral handoff rejected"):
            rt.partner_group_count_by_key(group_ids, 2, partner="numba")
        with self.assertRaisesRegex(RuntimeError, "Numba neutral handoff rejected"):
            rt.partner_group_sum_by_key(group_ids, values, 2, partner="numba")
        with self.assertRaisesRegex(RuntimeError, "Numba neutral handoff rejected"):
            rt.partner_group_min_by_key(group_ids, values, 2, partner="numba", initial=np.inf)
        with self.assertRaisesRegex(RuntimeError, "Numba neutral handoff rejected"):
            rt.partner_group_max_by_key(group_ids, values, 2, partner="numba", initial=-np.inf)

    def test_raydb_v2_6_descriptor_is_app_level_and_bounded(self) -> None:
        descriptor = raydb.describe_raydb_v2_6_numba_neutral_continuation("avg_as_sum_count")
        self.assertEqual(descriptor["selected_partner"], "numba")
        self.assertEqual(descriptor["operations"], ("segmented_sum_f64", "segmented_count_i64"))
        self.assertTrue(descriptor["uses_v2_6_neutral_partner_handoff"])
        self.assertFalse(descriptor["uses_legacy_torch_carrier"])
        self.assertFalse(descriptor["uses_torch_conversion"])
        self.assertFalse(descriptor["replaces_rt_traversal"])
        self.assertFalse(descriptor["public_speedup_claim_authorized"])
        self.assertFalse(descriptor["true_zero_copy_claim_authorized"])
        self.assertIn("RayDB query encoding remains Python app code", descriptor["app_owned_lowering"])

    def test_raydb_v2_6_descriptor_tracks_minmax_gap_closed_after_goal2995(self) -> None:
        descriptor = raydb.describe_raydb_v2_6_numba_neutral_continuation("min")
        self.assertEqual(descriptor["status"], "executable_for_count_sum_min_max")
        self.assertEqual(descriptor["operations"], ("segmented_min_f64",))
        self.assertIsNone(descriptor["blocked_reason"])

    def test_runner_uses_app_path_and_claim_boundary(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for phrase in (
            "run_raydb_v2_6_numba_neutral_continuation_preview",
            "avg_as_sum_count",
            "counts_match_cpu",
            "sums_match_cpu",
            "numba_cuda_module",
            "NUMBA_CUDA_USE_NVIDIA_BINDING",
            '"raydb_paper_reproduction_claim_authorized": False',
        ):
            self.assertIn(phrase, source)

    def test_report_records_prepared_status_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "first benchmark-app demonstrator",
            "RayDB-style grouped aggregate benchmark",
            "user-selected `partner=\"numba\"`",
            "post-RT continuation demonstrator",
            "not a full RayDB paper reproduction",
            "does not claim RT-core speedup",
            "min/max primitives",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
