from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1932_all_app_v2_pod_batch_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal1932_all_app_v2_pod_batch_runner_2026-05-13.md"


class Goal1932AllAppV2PodBatchRunnerTest(unittest.TestCase):
    def test_runner_has_visible_progress_and_all_key_steps(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("[goal1932]", text)
        self.assertIn("progress.log", text)
        self.assertIn("STEP_TIMEOUT_SECONDS", text)
        self.assertIn("timeout --preserve-status", text)
        self.assertIn("SOURCE_COMMIT_LABEL", text)
        self.assertIn("goal1925_fixed_radius_family_v2_partner_perf.py", text)
        self.assertIn("--source-commit-label", text)
        self.assertIn("--query-count-override", text)
        self.assertIn("--search-count-override", text)
        self.assertIn("ROBOT_POSE_COUNT", text)
        self.assertIn("ROBOT_OBSTACLE_COUNT", text)
        self.assertIn("SEGMENT_COUNTS", text)
        self.assertIn("goal1928_robot_collision_v2_partner_perf.py", text)
        self.assertIn("goal1856_segment_polygon_v2_partner_perf.py", text)
        self.assertIn("goal877_polygon_overlap_optix_phase_profiler.py", text)
        self.assertIn("goal756_db_prepared_session_perf.py", text)
        self.assertIn("goal982_graph_same_scale_timing_repair.py", text)
        self.assertIn("goal1931_current_all_app_v18_v2_perf_analysis.py", text)

    def test_runner_keeps_control_rows_named_as_controls(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("control_polygon_pair_overlap_area_rows", text)
        self.assertIn("control_polygon_set_jaccard", text)
        self.assertIn("control_database_analytics", text)
        self.assertIn("control_graph_analytics", text)
        self.assertNotIn("release_authorized=true", text)
        self.assertIn("goal1856_segment_polygon_anyhit_rows_${segment_count}", text)

    def test_report_documents_pod_command_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: runner-ready-pod-needed", text)
        self.assertIn("OUT_DIR=docs/reports/goal1932_all_app_v2_pod_batch", text)
        self.assertIn("STEP_TIMEOUT_SECONDS", text)
        self.assertIn("SEGMENT_COUNTS", text)
        self.assertIn("Evidence-only control rows", text)
        self.assertIn("not v2 partner speedup rows", text)
        self.assertIn("not a release action", text)


if __name__ == "__main__":
    unittest.main()
