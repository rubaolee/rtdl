from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3698_segment_pair_precision_guard_native_pod_validation_2026-06-07.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal3698_segment_pair_precision_guard_native_pod_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
PAIR_DIFF = ARTIFACT_DIR / "pair_set_diff_summary.json"
RAYJOIN_LOG = ARTIFACT_DIR / "rayjoin_lsi_dump.log"
RTDL_ROWS_HEAD = ARTIFACT_DIR / "rtdl_lsi_rows_head.json"


class Goal3698SegmentPairPrecisionGuardNativePodValidationTest(unittest.TestCase):
    def test_same_source_probe_repairs_lsi_count_gap(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        comparison = payload["comparison"]

        self.assertEqual(payload["rtdl_source_commit_short"], "e8e700ae")
        self.assertFalse(payload["goal3691_scoped_source_dirty"])
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual(comparison["rayjoin_lsi_intersections"], 20860)
        self.assertEqual(comparison["rayjoin_lsi_check_intersections"], 20860)
        self.assertEqual(comparison["rtdl_lsi_row_count"], 20860)
        self.assertEqual(comparison["lsi_count_delta_rtdl_minus_rayjoin"], 0)
        self.assertGreater(comparison["pip_query_speedup_rtdl_vs_rayjoin"], 1.0)
        self.assertLess(comparison["lsi_query_speedup_rtdl_vs_rayjoin"], 1.0)

    def test_pair_set_parity_is_clean_after_normalization(self) -> None:
        payload = json.loads(PAIR_DIFF.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3698.segment_pair_precision_guard_native_pair_parity.v1")
        self.assertEqual(payload["rtdl_commit_short"], "e8e700ae")
        self.assertEqual(payload["normalization"], "rtdl_left_id_minus_1_and_rtdl_right_id_minus_1")
        self.assertEqual(payload["rayjoin_count"], 20860)
        self.assertEqual(payload["rtdl_count"], 20860)
        self.assertEqual(payload["rtdl_payload_row_count"], 20860)
        self.assertEqual(payload["missing_count"], 0)
        self.assertEqual(payload["extra_count"], 0)
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])

    def test_logs_and_row_sample_are_present(self) -> None:
        log = RAYJOIN_LOG.read_text(encoding="utf-8")
        rows = json.loads(RTDL_ROWS_HEAD.read_text(encoding="utf-8"))

        self.assertIn("Intersections: 20860", log)
        self.assertIn("queries: 251011", log)
        self.assertGreaterEqual(len(rows), 10)
        self.assertIn("left_id", rows[0])
        self.assertIn("right_id", rows[0])

    def test_report_keeps_correctness_and_performance_separate(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("correctness repair validation, not a performance closeout", report)
        self.assertIn("Missing from RTDL | `0`", report)
        self.assertIn("RTDL query (s)", report)
        self.assertIn("still much slower than RayJoin", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
