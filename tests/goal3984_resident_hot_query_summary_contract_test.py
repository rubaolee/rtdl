import unittest
from pathlib import Path

from src.rtdsl.current_benchmark_scale_profiles import (
    CURRENT_BENCHMARK_SCALE_PROFILES,
    validate_current_benchmark_scale_profiles,
)


ROOT = Path(__file__).resolve().parents[1]
RAYDB_APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "raydb_style" / "rtdl_raydb_style_benchmark_app.py"
ROBOT_APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "robot_collision" / "rtdl_robot_collision_benchmark_app.py"


class Goal3984ResidentHotQuerySummaryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profiles = {profile.row_id: profile for profile in CURRENT_BENCHMARK_SCALE_PROFILES}
        cls.raydb_source = RAYDB_APP.read_text(encoding="utf-8")
        cls.robot_source = ROBOT_APP.read_text(encoding="utf-8")

    def test_registry_still_validates(self) -> None:
        self.assertEqual(validate_current_benchmark_scale_profiles()["status"], "accept")

    def test_raydb_high_repeat_profile_uses_compact_hot_path_total(self) -> None:
        profile = self.profiles["raydb_style_optix_count_scale_default_262k"]
        self.assertIn("--summary-only-iterations", profile.command)
        self.assertEqual(profile.command[profile.command.index("--repeat") + 1], "5000")
        self.assertEqual(profile.command[profile.command.index("--warmup") + 1], "50")
        self.assertEqual(
            profile.representative_hot_path_metric,
            "metadata.prepared_phase_timing_summary.native_call_wall.total_sec",
        )
        self.assertEqual(profile.hot_path_duration_target_sec, 1.0)
        self.assertEqual(profile.scale_calibration_status, "resident_high_repeat_summary_contract_goal3984")

    def test_robot_high_repeat_profile_uses_compact_hot_path_total(self) -> None:
        profile = self.profiles["robot_collision_optix_scale_default_1024_no_probe_reference"]
        self.assertIn("--summary-only-runs", profile.command)
        self.assertEqual(profile.command[profile.command.index("--repeats") + 1], "50000")
        self.assertEqual(profile.command[profile.command.index("--warmup") + 1], "100")
        self.assertEqual(
            profile.representative_hot_path_metric,
            "run_summary.phase_timing_seconds.traversal.total_sec",
        )
        self.assertEqual(profile.hot_path_duration_target_sec, 1.0)
        self.assertEqual(profile.scale_calibration_status, "resident_high_repeat_summary_contract_goal3984")

    def test_raydb_runner_exposes_suppressed_iteration_summary_fields(self) -> None:
        for fragment in [
            "--summary-only-iterations",
            "prepared_iteration_wall_sec_suppressed",
            "prepared_iteration_wall_summary",
            "prepared_phase_timing_summary",
        ]:
            self.assertIn(fragment, self.raydb_source)

    def test_robot_runner_exposes_suppressed_run_summary_fields(self) -> None:
        for fragment in [
            "--summary-only-runs",
            "run_details_suppressed",
            "run_summary",
            "prepared_run_index_summary",
            "prepared_query_run_index_summary",
        ]:
            self.assertIn(fragment, self.robot_source)

    def test_report_exists_and_keeps_claim_boundary(self) -> None:
        report = ROOT / "docs" / "reports" / "goal3984_resident_hot_query_summary_contract_2026-06-08.md"
        text = report.read_text(encoding="utf-8")
        for fragment in [
            "resident high-repeat hot-query summary",
            "does not authorize public speedup",
            "Wrapper elapsed remains pod-budget evidence",
            "not a loader or OptiX SDK issue",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
