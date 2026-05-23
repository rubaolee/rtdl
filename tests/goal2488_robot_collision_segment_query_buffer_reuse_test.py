from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import unittest

from rtdsl import prepare_embree_static_triangle_scene_3d
from rtdsl import prepare_grouped_segment_query_3d
from rtdsl.reference import Triangle3D


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "robot_collision"
    / "rtdl_robot_collision_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal2488_robot_collision_segment_query_buffer_reuse_2026-05-21.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2488_robot_collision_segment_query_buffer_reuse_pod" / "summary.json"
ACTIVE_NATIVE_DIRS = (
    ROOT / "src" / "native" / "embree",
    ROOT / "src" / "native" / "optix",
)
FORBIDDEN_NATIVE_WORDS = ("robot", "collision", "link", "pose", "joint", "kinematic", "planner")
FORBIDDEN_NATIVE_RE = re.compile(
    r"\b(robot|collision|link|pose|joint|kinematic|planner)\b",
    re.IGNORECASE,
)
CONTRACT = "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1"


TRIANGLES = (
    Triangle3D(1, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 2.0, 0.0),
)
SEGMENT_STARTS = (
    (0.25, 0.25, 1.0),
    (2.5, 2.5, 1.0),
    (2.5, 0.25, 1.0),
    (0.75, 0.25, 1.0),
    (0.3333333333333333, 0.3333333333333333, 2.0),
)
SEGMENT_ENDS = (
    (0.25, 0.25, -1.0),
    (2.5, 2.5, -1.0),
    (2.5, 0.25, -1.0),
    (0.75, 0.25, -1.0),
    (0.3333333333333333, 0.3333333333333333, -2.0),
)
GROUP_OFFSETS = (0, 1, 2, 4, 4, 5)
EXPECTED_FLAGS = [1, 0, 1, 0, 1]


class Goal2488RobotCollisionSegmentQueryBufferReuseTest(unittest.TestCase):
    def test_prepared_grouped_segment_query_descriptor_is_app_agnostic_and_host_scoped(self) -> None:
        query = prepare_grouped_segment_query_3d(SEGMENT_STARTS, SEGMENT_ENDS, GROUP_OFFSETS)
        descriptor = query.descriptor()

        self.assertEqual(descriptor["contract"], CONTRACT)
        self.assertEqual(descriptor["segment_count"], len(SEGMENT_STARTS))
        self.assertEqual(descriptor["group_count"], len(GROUP_OFFSETS) - 1)
        self.assertEqual(descriptor["copy_boundary"], "python_ctypes_host_buffer")
        self.assertTrue(descriptor["host_query_buffers_reused"])
        self.assertTrue(descriptor["host_output_buffer_reused"])
        self.assertFalse(descriptor["native_device_query_buffers_reused"])
        self.assertFalse(descriptor["true_zero_copy_authorized"])
        self.assertFalse(descriptor["public_speedup_claim_authorized"])

    def test_embree_prepared_scene_can_reuse_prepared_query_and_output_host_buffers(self) -> None:
        query = prepare_grouped_segment_query_3d(SEGMENT_STARTS, SEGMENT_ENDS, GROUP_OFFSETS)
        with prepare_embree_static_triangle_scene_3d(TRIANGLES) as prepared:
            first = prepared.run_prepared_grouped_segment_any_hit_flags(query)
            second = prepared.run_prepared_grouped_segment_any_hit_flags(query)

        self.assertEqual(first["flags"], EXPECTED_FLAGS)
        self.assertEqual(second["flags"], EXPECTED_FLAGS)
        self.assertEqual(first["prepared_query_run_index"], 1)
        self.assertEqual(second["prepared_query_run_index"], 2)
        self.assertTrue(second["host_query_output_buffers_reused"])
        self.assertFalse(second["native_query_output_buffers_reused"])
        self.assertEqual(second["phase_timing_seconds"]["query_pack"], 0.0)
        self.assertGreaterEqual(second["phase_timing_seconds"]["output_clear"], 0.0)
        self.assertFalse(second["claim_boundary"]["true_zero_copy"])

    def test_robot_collision_cli_exposes_prepared_buffer_mode_without_speedup_claim(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(APP),
                "--mode",
                "embree_prepared_buffers",
                "--dataset",
                "tiny",
                "--repeats",
                "3",
                "--warmup",
                "1",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)
        reuse = payload["reuse_metadata"]

        self.assertEqual(payload["goal"], "Goal2488")
        self.assertEqual(payload["mode"], "embree_prepared_buffers")
        self.assertTrue(reuse["host_query_output_buffers_reused"])
        self.assertFalse(reuse["native_query_output_buffers_reused"])
        self.assertEqual(reuse["prepared_query_run_indices"], [1, 2, 3])
        self.assertTrue(reuse["prepared_query_run_indices_strictly_increase"])
        self.assertEqual(reuse["prepared_query_descriptor"]["copy_boundary"], "python_ctypes_host_buffer")
        self.assertFalse(reuse["prepared_query_descriptor"]["true_zero_copy_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_active_native_targets_still_do_not_contain_robot_app_vocabulary(self) -> None:
        hits: list[str] = []
        for directory in ACTIVE_NATIVE_DIRS:
            for path in directory.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if FORBIDDEN_NATIVE_RE.search(text):
                    hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])

    def test_report_records_scope_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2488 is complete", report)
        self.assertIn("host-side reusable query buffer", report)
        self.assertIn("No native C++/CUDA files were changed", report)
        self.assertIn("does not claim true zero-copy", report)
        self.assertIn("OptiX still uploads query segments per run", report)
        self.assertIn("next implementation gate", report)

    def test_pod_summary_records_optix_prepared_buffer_validation(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(summary["goal"], "Goal2488")
        self.assertEqual(summary["gpu"], "NVIDIA RTX 4000 Ada Generation")
        self.assertTrue(summary["buffers_all_match"])
        self.assertTrue(summary["buffers_host_query_output_buffers_reused"])
        self.assertFalse(summary["buffers_native_query_output_buffers_reused"])
        self.assertEqual(summary["optix_prepared_buffers_query_pack_median"], 0.0)
        self.assertGreater(summary["optix_prepared_query_pack_median"], 0.0)
        self.assertGreater(summary["total_median_ratio_prepared_over_buffers"], 1.0)


if __name__ == "__main__":
    unittest.main()
