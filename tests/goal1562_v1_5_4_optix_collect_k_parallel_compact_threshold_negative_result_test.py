from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1562_v1_5_4_optix_collect_k_parallel_compact_threshold_negative_result_2026-05-08.md"
CONTROL = ROOT / "docs" / "reports" / "goal1562_v1_5_4_optix_collect_k_threshold_4096_control_2026-05-08.json"
TRANSCRIPT = ROOT / "docs" / "reports" / "goal1562_v1_5_4_optix_collect_k_threshold_matrix_failure_2026-05-08.txt"


class Goal1562V154OptixCollectKParallelCompactThresholdNegativeResultTest(unittest.TestCase):
    def test_default_threshold_control_remains_valid(self) -> None:
        data = json.loads(CONTROL.read_text(encoding="utf-8"))

        self.assertTrue(data["accepted_goal1506_evidence"])
        for case in data["cases"]:
            self.assertTrue(case["same_candidate_rows"])
            self.assertTrue(case["same_valid_count"])
            self.assertTrue(case["same_overflowed_flag"])

    def test_threshold_8192_failed_before_timing(self) -> None:
        text = TRANSCRIPT.read_text(encoding="utf-8")

        self.assertIn("THRESHOLD=4096", text)
        self.assertIn("THRESHOLD=8192", text)
        self.assertIn("warmup collect-k parity failed before timing", text)

    def test_report_rejects_threshold_tuning_shortcut(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Do not tune", text)
        self.assertIn("failed warmup parity", text)
        self.assertIn("No timing claim is valid", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
