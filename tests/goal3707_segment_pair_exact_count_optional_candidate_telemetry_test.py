from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs/reports/goal3707_segment_pair_exact_count_optional_candidate_telemetry_2026-06-07.md"


class Goal3707SegmentPairExactCountOptionalCandidateTelemetryTest(unittest.TestCase):
    def test_anyhit_candidate_event_counter_is_optional(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        block = source.split("static void ensure_segment_pair_exact_count_pipeline", 1)[1].split(
            "static void ensure_segment_pair_ambiguity_count_kernel",
            1,
        )[0]

        self.assertIn("params.candidate_event_count != nullptr", block)
        self.assertIn("atomicAdd(params.candidate_event_count, 1ull)", block)
        self.assertIn("new_write_without_mandatory_candidate_counter", block)

    def test_exact_count_helper_has_explicit_telemetry_flag(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        block = source.split("static size_t count_segment_pair_intersection_exact_one_pass_optix", 1)[1].split(
            "static void run_prepared_segment_pair_candidate_device_columns_optix",
            1,
        )[0]

        self.assertIn("bool record_candidate_events", block)
        self.assertIn("record_candidate_events ? sizeof(unsigned long long) : 0", block)
        self.assertIn("if (record_candidate_events)", block)
        self.assertIn("g_optix_last_segment_pair_raw_candidate_count = 0;", block)

    def test_selected_routes_keep_candidate_telemetry_enabled_after_negative_probe(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        count_block = source.split("static void count_prepared_segment_pair_intersection_optix", 1)[1].split(
            "static void count_prepared_segment_pair_intersection_prepared_left_optix",
            1,
        )[0]
        prepared_left_block = source.split(
            "static void count_prepared_segment_pair_intersection_prepared_left_optix",
            1,
        )[1].split("static void run_prepared_segment_first_hit_optix", 1)[0]

        self.assertIn("prepared->accel.handle,\n        true)", count_block)
        self.assertIn("prepared->accel.handle,\n        true)", prepared_left_block)

    def test_report_keeps_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("candidate-event telemetry optional", report)
        self.assertIn("optional no-telemetry path remains available", report)
        self.assertIn("Goal3708 negative pod probe", report)
        self.assertIn("not an app-specific shortcut", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
