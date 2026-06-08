from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "robot_collision"
    / "rtdl_robot_collision_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal3904_robot_collision_standard_timing_aliases_2026-06-08.md"


class Goal3904RobotCollisionStandardTimingAliasesTest(unittest.TestCase):
    def test_prepared_payload_emits_standard_timing_aliases(self) -> None:
        from examples.v2_0.research_benchmarks.robot_collision.rtdl_robot_collision_benchmark_app import (
            run_prepared_reuse_probe,
        )
        from scripts.goal3828_current_benchmark_scale_profile_runner import _payload_timing_summary

        payload = run_prepared_reuse_probe(backend="embree", dataset="tiny", repeats=4, warmup=1)
        timing = payload["benchmark_timing_sec"]
        self.assertIn("app_lowering_sec", timing)
        self.assertIn("tail_total_run_sec", timing)
        self.assertIn("probe_reference_sec", timing)
        self.assertIn("tail_phase_prepare_build_sec", timing)
        self.assertIn("tail_phase_query_pack_sec", timing)
        self.assertIn("tail_phase_traversal_sec", timing)
        self.assertEqual(timing["tail_total_run_sec"], payload["tail_medians"]["total_run_seconds"])
        self.assertEqual(
            timing["tail_phase_traversal_sec"],
            payload["tail_medians"]["phase_timing_seconds"]["traversal"],
        )

        summary = _payload_timing_summary(payload)
        paths = {item["path"] for item in summary["timing_scalars_sample"]}
        self.assertGreaterEqual(summary["timing_scalar_count"], 5)
        self.assertIn("$.benchmark_timing_sec.tail_total_run_sec", paths)
        self.assertIn("$.benchmark_timing_sec.tail_phase_traversal_sec", paths)

    def test_change_is_app_layer_only_and_boundary_documented(self) -> None:
        source = APP.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn('"benchmark_timing_sec"', source)
        self.assertIn("tail_phase_", source)
        self.assertIn("No native source file", report)
        self.assertIn("not a performance optimization", report)
        self.assertIn("does not authorize release action", report)


if __name__ == "__main__":
    unittest.main()
