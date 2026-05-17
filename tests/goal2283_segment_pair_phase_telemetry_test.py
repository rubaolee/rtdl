from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2283_segment_pair_phase_telemetry_2026-05-17.md"


class Goal2283SegmentPairPhaseTelemetryTest(unittest.TestCase):
    def test_native_symbol_is_declared_and_implemented(self) -> None:
        symbol = "rtdl_optix_segment_pair_intersection_get_last_phase_timings"

        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, WORKLOADS.read_text(encoding="utf-8"))

    def test_workloads_record_expected_phase_fields(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        for field in (
            "g_optix_last_segment_pair_left_upload_s",
            "g_optix_last_segment_pair_candidate_count_s",
            "g_optix_last_segment_pair_candidate_write_s",
            "g_optix_last_segment_pair_candidate_download_s",
            "g_optix_last_segment_pair_exact_refine_s",
            "g_optix_last_segment_pair_raw_candidate_count",
            "g_optix_last_segment_pair_emitted_count",
            "g_optix_last_segment_pair_mode",
        ):
            self.assertIn(field, text)
        self.assertIn("reset_segment_pair_phase_timings(1u)", text)
        self.assertIn("reset_segment_pair_phase_timings(2u)", text)
        self.assertIn("std::chrono::steady_clock::now()", text)

    def test_python_runtime_exposes_global_and_prepared_accessors(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def get_last_segment_pair_phase_timings()", text)
        self.assertIn("def _get_last_segment_pair_phase_timings_from_library", text)
        self.assertIn("def last_phase_timings(self) -> dict[str, float | int | str] | None:", text)
        for key in (
            '"mode"',
            '"left_upload"',
            '"candidate_count_pass"',
            '"candidate_write_pass"',
            '"candidate_download"',
            '"exact_refine"',
            '"raw_candidate_count"',
            '"emitted_count"',
        ):
            self.assertIn(key, text)

    def test_report_keeps_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("instrumentation, not an optimization", text)
        self.assertIn("does not authorize a speedup claim", text)
        self.assertIn("without", text)
        self.assertIn("adding RayJoin-specific native engine logic", text)
        self.assertIn("bottleneck diagnosis", text)


if __name__ == "__main__":
    unittest.main()
