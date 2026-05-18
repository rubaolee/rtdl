from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2327_rayjoin_perf_tuning_round1_2026-05-18.md"
RUNNER = ROOT / "scripts" / "goal2327_rayjoin_pod_perf_runner.sh"
SUMMARY = ROOT / "scripts" / "goal2327_rayjoin_pod_artifact_summary.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2327RayJoinPerfTuningPacketTest(unittest.TestCase):
    def test_report_tracks_all_six_rayjoin_perf_workstreams(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "Generic device-resident row stream / continuation",
            "Generic grouped count/parity reduction",
            "Stronger prepared closed-shape membership",
            "Many-query batching and launch grouping",
            "Phase-separated timing",
            "Paper-protocol reproduction discipline",
        ]:
            self.assertIn(phrase, text)
        self.assertIn("local-prep-complete-pod-needed", text)
        self.assertIn("Overlay remains deliberately excluded", text)

    def test_pod_runner_has_progress_timeout_and_claim_boundary(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("STEP_TIMEOUT_SECONDS", text)
        self.assertIn("log \"START", text)
        self.assertIn("timeout \"${STEP_TIMEOUT_SECONDS}\"", text)
        self.assertIn("LSI_STREAM", text)
        self.assertIn("PIP_STREAM", text)
        self.assertIn("goal2327_rayjoin_pod_artifact_summary.py", text)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": false', text)

    def test_pod_summary_script_keeps_tables_and_claim_boundary_visible(self) -> None:
        text = SUMMARY.read_text(encoding="utf-8")
        self.assertIn("Fixture Prepared OptiX Route", text)
        self.assertIn("Same-Query Stream Replay", text)
        self.assertIn("claim_boundary.json", text)
        self.assertIn("does not authorize", text)

    def test_public_rayjoin_readme_teaches_prepared_route(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("--execution-route prepared_optix", text)
        self.assertIn("--result-mode count", text)
        self.assertIn("device-resident", text)
        self.assertIn("continuation primitive", text)

    def test_future_todo_records_reopened_benchmark_priority_without_app_native_shortcut(self) -> None:
        text = TODO.read_text(encoding="utf-8")
        self.assertIn("reopened RayJoin as the top benchmark-app performance", text)
        self.assertIn("Do not solve the gap by reintroducing RayJoin-specific native kernels.", text)


if __name__ == "__main__":
    unittest.main()
