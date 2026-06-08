from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3995_grouped_union_telemetry_metadata_clarification_2026-06-08.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3994_claude_review_goal3992_grouped_union_extended_telemetry_2026-06-08.md"


class Goal3995GroupedUnionTelemetryMetadataClarificationTest(unittest.TestCase):
    def test_runtime_distinguishes_buffer_capacity_from_populated_counters(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("telemetry_buffer_length =", runtime)
        self.assertIn("use_extended_telemetry = telemetry_buffer_length >= 8", runtime)
        self.assertIn(
            "8 if use_extended_telemetry else (4 if telemetry_handoff is not None else 0)",
            runtime,
        )
        self.assertIn('"grouped_union_telemetry_buffer_length": telemetry_buffer_length', runtime)
        self.assertIn('"grouped_union_telemetry_counter_count": telemetry_counter_count', runtime)
        self.assertIn("ctypes.c_size_t(telemetry_buffer_length)", runtime)
        self.assertNotIn("ctypes.c_size_t(telemetry_counter_count)", runtime)

    def test_report_closes_claude_minor_observation_without_overclaim(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIn("Minor Observation", review)
        for fragment in [
            "buffer_length",
            "counter_count",
            "5-, 6-, or 7-counter buffer",
            "old 4-counter ABI",
            "No native ABI change",
            "No performance claim",
            "does not authorize public speedup wording",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
