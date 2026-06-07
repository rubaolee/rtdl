from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs/reports/goal3705_segment_pair_prepared_left_exact_count_pod_a5000/summary.json"
REPORT = ROOT / "docs/reports/goal3705_segment_pair_prepared_left_exact_count_pod_validation_2026-06-07.md"


class Goal3705SegmentPairPreparedLeftExactCountPodValidationTest(unittest.TestCase):
    def test_same_source_lsi_count_remains_fixed(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        comparison = payload["comparison"]

        self.assertEqual(payload["rtdl_source_commit_short"], "d9ec70b3")
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual(comparison["rayjoin_lsi_check_intersections"], 20860)
        self.assertEqual(comparison["rayjoin_lsi_intersections"], 20860)
        self.assertEqual(comparison["rtdl_lsi_row_count"], 20860)
        self.assertEqual(comparison["lsi_count_delta_rtdl_minus_rayjoin"], 0)

    def test_prepared_left_phase_shape_removes_left_upload(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        lsi = payload["rtdl"]["lsi"]
        phases = lsi["native_phase_timings"]

        self.assertTrue(lsi["prepared_left_for_count"])
        self.assertEqual(lsi["segment_policy"], "device_double_exact_count_during_optix_anyhit")
        self.assertEqual(lsi["row_count"], 20860)
        self.assertEqual(phases["mode"], "count_prepared_left")
        self.assertEqual(phases["left_upload"], 0.0)
        self.assertEqual(phases["candidate_write_pass"], 0.0)
        self.assertEqual(phases["candidate_download"], 0.0)
        self.assertEqual(phases["exact_refine"], 0.0)
        self.assertEqual(phases["raw_candidate_count"], 20972)
        self.assertEqual(phases["emitted_count"], 20860)
        self.assertGreater(phases["candidate_count_pass"], 0.0)

    def test_timing_is_close_but_does_not_beat_rayjoin(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        comparison = payload["comparison"]
        rtdl_lsi = payload["rtdl"]["lsi"]

        self.assertLess(rtdl_lsi["hot_median_sec"], 0.004467187449336052)
        self.assertGreater(comparison["lsi_query_speedup_rtdl_vs_rayjoin"], 0.8)
        self.assertLess(comparison["lsi_query_speedup_rtdl_vs_rayjoin"], 1.0)
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])

    def test_report_keeps_close_to_rayjoin_and_not_faster_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("performance-improvement validation, not a RayJoin closeout", report)
        self.assertIn("`0.834x`", report)
        self.assertIn("RayJoin remains faster", report)
        self.assertIn("avoid both candidate materialization and per-query left upload", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
