from __future__ import annotations

import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "robot_collision"
    / "rtdl_robot_collision_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal2491_robot_collision_benchmark_app_closeout_2026-05-22.md"
GOAL = ROOT / "docs" / "reports" / "goal2491_finish_robot_collision_benchmark_app_goal_2026-05-22.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2491_robot_collision_finish_pod" / "summary.json"
LOCAL_MATRIX = ROOT / "docs" / "reports" / "goal2491_robot_collision_finish_local_matrix.json"
NATIVE_DIRS = (
    ROOT / "src" / "native" / "embree",
    ROOT / "src" / "native" / "optix",
)
FORBIDDEN_NATIVE_RE = re.compile(
    r"\b(robot|collision|link|pose|joint|kinematic|planner)\b",
    re.IGNORECASE,
)
CANONICAL_MODES = {
    "cpu_reference",
    "embree_prepared",
    "embree_prepared_buffers",
    "optix_prepared",
    "optix_prepared_buffers",
    "optix_prepared_device_buffers",
    "optix_prepared_device_count",
}


def _row_by_mode(rows: list[dict[str, object]], mode: str) -> dict[str, object]:
    return next(row for row in rows if row.get("mode") == mode)


class Goal2491RobotCollisionBenchmarkAppCloseoutTest(unittest.TestCase):
    def test_goal_and_report_record_finish_scope(self) -> None:
        goal = GOAL.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Finish the robot-collision benchmark app", goal)
        self.assertIn("Goal2491 closes", report)
        self.assertIn("sampled discrete feasibility", report)
        self.assertIn("continuous or swept-volume collision", report)
        self.assertIn("no robot-specific native ABI", report)
        self.assertIn("public speedup claims", report)

    def test_app_exposes_final_matrix_modes(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn("--final-matrix", app)
        self.assertIn("final_canonical_robot_collision_modes", app)
        for mode in CANONICAL_MODES:
            self.assertIn(mode, app)

    def test_pod_summary_records_all_final_rows(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))
        rows = summary["rows"]

        self.assertEqual(summary["goal"], "Goal2491")
        self.assertEqual({row["mode"] for row in rows}, CANONICAL_MODES)
        for row in rows:
            self.assertEqual(row["status"], "ok", row)

        for mode in CANONICAL_MODES - {"cpu_reference"}:
            row = _row_by_mode(rows, mode)
            self.assertTrue(row["all_measured_counts_match_probe_reference"], row)
            self.assertTrue(row["all_measured_runs_match_probe_reference"], row)

        matrix_row = _row_by_mode(summary["matrix"]["rows"], "optix_prepared_device_count")
        descriptor = matrix_row["reuse_metadata"]["prepared_query_descriptor"]
        self.assertEqual(descriptor["result_kind"], "uint32_flagged_group_count")
        self.assertFalse(descriptor["python_group_flags_materialized"])
        self.assertFalse(descriptor["true_zero_copy_authorized"])

    def test_local_matrix_records_embree_evidence(self) -> None:
        matrix = json.loads(LOCAL_MATRIX.read_text(encoding="utf-8"))
        rows = matrix["rows"]

        self.assertEqual(matrix["goal"], "Goal2491")
        self.assertEqual(matrix["matrix_scope"], "final_canonical_robot_collision_modes")
        self.assertEqual(_row_by_mode(rows, "embree_prepared")["status"], "ok")
        self.assertEqual(_row_by_mode(rows, "embree_prepared_buffers")["status"], "ok")
        self.assertTrue(_row_by_mode(rows, "embree_prepared_buffers")["all_measured_runs_match_probe_reference"])

    def test_native_files_remain_app_vocabulary_free(self) -> None:
        hits: list[str] = []
        for directory in NATIVE_DIRS:
            for path in directory.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if FORBIDDEN_NATIVE_RE.search(text):
                    hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
