from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5259_modelnet40_first3_hd_exec_batch_exact_witness_pod.json"
)


class Goal5259XhdRtdlHdExecModelNet40BatchPodArtifactTest(unittest.TestCase):
    def test_first3_batch_bridge_artifact(self) -> None:
        if not RESULT.exists():
            self.skipTest(f"missing POD artifact: {RESULT}")
        payload = json.loads(RESULT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.rtdl_hd_exec_summary_batch.v1")
        self.assertEqual(payload["selected_case_count"], 3)
        self.assertEqual(payload["matched_case_count"], 3)
        self.assertEqual(payload["failed_case_count"], 0)
        self.assertTrue(payload["all_cases_matched"])
        self.assertFalse(payload["claim_boundary"]["bulk_all400_claimed"])
        self.assertFalse(payload["claim_boundary"]["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["author_performance_parity_claimed"])

        expected_names = [
            "0000_airplane_0036__airplane_0515",
            "0001_airplane_0144__airplane_0384",
            "0002_airplane_0384__airplane_0569",
        ]
        self.assertEqual([case["case_name"] for case in payload["cases"]], expected_names)
        for case in payload["cases"]:
            self.assertEqual(case["route_label"], "cell-mbr-exact-witness")
            self.assertTrue(case["matched_author"])
            self.assertLessEqual(case["author_abs_diff"], 1e-6)
            self.assertTrue(case["per_source_witness_exact"])
            self.assertIn("RTDL route wall time", case["running_time_semantics"])
            self.assertEqual(case["reference_preprocessing"], ["normalize_each_input_to_author_float32_unit_box"])


if __name__ == "__main__":
    unittest.main()
