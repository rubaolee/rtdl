from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

import rtdsl as rt
from examples.v2_0.research_benchmarks.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as triangle,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
APP = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2999_triangle_counting_numba_compact_mask_wiring_2026-06-01.md"
)
READINESS = REPO_ROOT / "src" / "rtdsl" / "v2_5_internal_readiness.py"


class Goal2999TriangleCountingNumbaCompactMaskWiringTest(unittest.TestCase):
    def test_plan_exposes_numba_compact_mask_without_replacing_scalar_fast_path(self) -> None:
        payload = triangle.run_app("v2_6_numba_compact_mask_plan")

        self.assertEqual(payload["app"], "triangle_counting")
        self.assertEqual(payload["selected_partner"], "numba")
        self.assertEqual(payload["operation"], "compact_mask_i64")
        self.assertEqual(payload["numba_descriptor"]["operation"], "compact_mask_i64")
        self.assertEqual(
            payload["input_columns"],
            ("candidate_row_ids:int64", "valid_triangle_mask:bool"),
        )
        self.assertTrue(payload["uses_v2_6_neutral_partner_handoff"])
        self.assertTrue(payload["uses_v2_8_segmented_typed_stream_front_door"])
        self.assertFalse(payload["uses_legacy_torch_carrier"])
        self.assertFalse(payload["uses_torch_conversion"])
        self.assertTrue(payload["fast_scalar_summary_path_unchanged"])
        self.assertFalse(payload["replaces_rt_traversal"])
        self.assertFalse(payload["promoted_performance_path"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])

    def test_preview_rejects_host_numpy_arrays_before_cuda_execution(self) -> None:
        inputs = {
            "candidate_row_ids": np.asarray([10, 11, 12, 13], dtype=np.int64),
            "valid_triangle_mask": np.asarray([False, True, True, False], dtype=np.bool_),
        }
        with self.assertRaisesRegex(ValueError, "device-resident CUDA column is required"):
            triangle.run_triangle_counting_v2_6_numba_compact_mask_preview(inputs)

    def test_app_source_uses_v2_8_front_door_and_no_goal2998_collision(self) -> None:
        source = APP.read_text(encoding="utf-8")
        for phrase in (
            "TRIANGLE_COUNTING_V2_6_NUMBA_COMPACT_MASK_VERSION",
            "describe_triangle_counting_v2_6_numba_compact_mask_continuation",
            "run_triangle_counting_v2_6_numba_compact_mask_preview",
            "prepare_v2_6_neutral_partner_handoff",
            "build_segmented_typed_stream_adapter",
            "execute_segmented_typed_stream_partner_continuation",
            "v2_8_segmented_typed_stream_front_door_used",
            "v2_6_numba_compact_mask_plan",
        ):
            self.assertIn(phrase, source)
        self.assertNotIn("rt.run_numba_compact_mask_i64(", source)
        readiness = READINESS.read_text(encoding="utf-8")
        self.assertIn("begin_goal2999_numba_compact_mask_benchmark_app_wiring_after_goal2998_review", readiness)
        self.assertNotIn("begin_goal2998_numba_compact_mask_benchmark_app_wiring_after_review", readiness)

    def test_v2_6_roadmap_indexes_goal2999_without_speedup_claim(self) -> None:
        roadmap = rt.v2_6_roadmap()

        self.assertEqual(roadmap["triangle_compact_mask_goal"], "Goal2999")
        self.assertIn("triangle_counting", roadmap["triangle_compact_mask_status"])
        self.assertIn("not_speedup_evidence", roadmap["triangle_compact_mask_status"])
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_report_records_app_level_wiring_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal2999",
            "compact_mask_i64",
            "triangle counting",
            "fused generic RTDL ray/triangle summary",
            "host NumPy arrays fail closed",
            "not a speedup claim",
            "CUDA pod runtime evidence is still pending",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
