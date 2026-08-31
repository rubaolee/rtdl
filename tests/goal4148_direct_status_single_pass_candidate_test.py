from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4148_direct_status_single_pass_candidate_2026-06-09.md"


class Goal4148DirectStatusSinglePassCandidateTest(unittest.TestCase):
    def test_runtime_exposes_explicit_candidate_without_changing_default(self) -> None:
        source = RUNTIME.read_text(encoding="utf-8")

        self.assertIn('convergence_mode: str = "until_stable"', source)
        self.assertIn('"single_pass_candidate"', source)
        self.assertIn('iteration_limit = 1 if convergence_mode == "single_pass_candidate"', source)
        self.assertIn('"direct_status_convergence_proven": bool(convergence_proven)', source)
        self.assertIn('"direct_status_single_pass_candidate": convergence_mode == "single_pass_candidate"', source)

    def test_app_cli_requires_user_selection_and_blocks_promotion(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--direct-status-convergence-mode", source)
        self.assertIn('direct_status_convergence_mode: str = "until_stable"', source)
        self.assertIn('"direct_status_convergence_mode_user_selection": direct_status_convergence_mode', source)
        self.assertIn('"direct_status_convergence_mode_default_route_changed": False', source)
        self.assertIn('"direct_status_single_pass_promoted": False', source)

    def test_report_records_pod_needed_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "implementation-complete-pod-measured-in-goal4149",
            "default remains `until_stable`",
            "not a route promotion",
            "single-pass candidate",
            "does not authorize release",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
