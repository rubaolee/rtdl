from __future__ import annotations

import json
from pathlib import Path
import statistics
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json"
)


class Goal5260XhdHdExecAll400BatchArtifactTest(unittest.TestCase):
    def test_all400_hd_exec_batch_artifact(self) -> None:
        if not RESULT.exists():
            self.skipTest(f"missing POD artifact: {RESULT}")
        payload = json.loads(RESULT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.rtdl_hd_exec_summary_batch.v1")
        self.assertEqual(payload["selected_case_count"], 400)
        self.assertEqual(payload["matched_case_count"], 400)
        self.assertEqual(payload["failed_case_count"], 0)
        self.assertTrue(payload["all_cases_matched"])
        self.assertEqual(payload["route_label"], "cell-mbr-exact-witness")
        self.assertFalse(payload["claim_boundary"]["bulk_all400_claimed"])
        self.assertFalse(payload["claim_boundary"]["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["author_performance_parity_claimed"])

        absdiff = [float(case["author_abs_diff"]) for case in payload["cases"]]
        times = [float(case["running_avg_time_ms"]) for case in payload["cases"]]
        self.assertLessEqual(max(absdiff), 1e-6)
        self.assertAlmostEqual(statistics.median(absdiff), 7.368051571643441e-09)
        self.assertGreater(statistics.median(times), 0.0)
        self.assertGreater(float(payload["elapsed_sec"]), 0.0)

        for case in payload["cases"]:
            self.assertEqual(case["route_label"], "cell-mbr-exact-witness")
            self.assertTrue(case["matched_author"])
            self.assertTrue(case["per_source_witness_exact"])
            self.assertIn("RTDL route wall time", case["running_time_semantics"])
            self.assertEqual(case["reference_preprocessing"], ["normalize_each_input_to_author_float32_unit_box"])


if __name__ == "__main__":
    unittest.main()
