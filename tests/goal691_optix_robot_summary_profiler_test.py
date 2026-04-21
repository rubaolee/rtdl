from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_json(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal691OptixRobotSummaryProfilerTest(unittest.TestCase):
    def test_robot_default_rows_mode_still_matches_oracle(self) -> None:
        payload = run_json("examples/rtdl_robot_collision_screening_app.py", "--backend", "cpu_python_reference")
        self.assertEqual(payload["optix_summary_mode"], "rows")
        self.assertTrue(payload["matches_oracle"])
        self.assertIn("edge_any_hit_rows", payload)

    def test_profiler_lists_optix_performance_classes(self) -> None:
        payload = run_json("scripts/goal691_optix_app_phase_profiler.py", "--list-apps")
        matrix = payload["optix_app_performance_matrix"]
        self.assertEqual(matrix["robot_collision_screening"]["performance_class"], "optix_traversal")
        self.assertEqual(matrix["graph_analytics"]["performance_class"], "host_indexed_fallback")
        self.assertEqual(matrix["hausdorff_distance"]["performance_class"], "cuda_through_optix")

    def test_profiler_runs_portable_robot_rows_mode(self) -> None:
        payload = run_json(
            "scripts/goal691_optix_app_phase_profiler.py",
            "--app",
            "robot_collision_screening",
            "--backend",
            "cpu_python_reference",
            "--iterations",
            "1",
        )
        self.assertEqual(payload["app"], "robot_collision_screening")
        self.assertEqual(payload["backend"], "cpu_python_reference")
        self.assertEqual(payload["summary_mode"], "rows")
        self.assertTrue(payload["last_output"]["matches_oracle"])
        self.assertIn("python_input_construction", payload["phase_stats"])

    def test_handoff_requests_exist_for_external_review_split(self) -> None:
        for rel_path in (
            "docs/handoff/GOAL691_CLAUDE_DB_SEGPOLY_OPTIX_ACTION_REQUEST_2026-04-21.md",
            "docs/handoff/GOAL691_GEMINI_CUDA_THROUGH_OPTIX_ACTION_REQUEST_2026-04-21.md",
        ):
            with self.subTest(path=rel_path):
                text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
                self.assertIn("goal689_optix_app_performance_review", text)
                self.assertIn("goal690_gemini_optix_consensus_action_plan", text)


if __name__ == "__main__":
    unittest.main()
