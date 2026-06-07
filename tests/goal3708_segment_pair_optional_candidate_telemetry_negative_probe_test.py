from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs/reports/goal3708_segment_pair_optional_candidate_telemetry_negative_pod_a5000/summary.json"
REPORT = ROOT / "docs/reports/goal3708_segment_pair_optional_candidate_telemetry_negative_probe_2026-06-07.md"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"


class Goal3708SegmentPairOptionalCandidateTelemetryNegativeProbeTest(unittest.TestCase):
    def test_negative_probe_remains_correct_but_slower_than_goal3705(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        comparison = payload["comparison"]
        lsi = payload["rtdl"]["lsi"]

        self.assertEqual(payload["rtdl_source_commit_short"], "c9305425")
        self.assertEqual(comparison["rayjoin_lsi_check_intersections"], 20860)
        self.assertEqual(comparison["rtdl_lsi_row_count"], 20860)
        self.assertEqual(comparison["lsi_count_delta_rtdl_minus_rayjoin"], 0)
        self.assertEqual(lsi["native_phase_timings"]["raw_candidate_count"], 0)
        self.assertGreater(lsi["hot_median_sec"], 0.0010864129289984703)
        self.assertLess(comparison["lsi_query_speedup_rtdl_vs_rayjoin"], 0.8339287722166602)

    def test_current_selected_prepared_left_route_reenables_candidate_telemetry(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        prepared_left_block = source.split(
            "static void count_prepared_segment_pair_intersection_prepared_left_optix",
            1,
        )[1].split("static void run_prepared_segment_first_hit_optix", 1)[0]

        self.assertIn("prepared->accel.handle,\n        true)", prepared_left_block)

    def test_report_records_negative_decision(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not help", report)
        self.assertIn("not selected", report)
        self.assertIn("Restore the selected prepared-left scalar-count route", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
