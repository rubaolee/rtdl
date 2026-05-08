import unittest
from pathlib import Path


REPORT = Path("docs/reports/goal1566_v1_5_4_optix_collect_k_output_indexed_merge_path_design_2026-05-08.md")


class Goal1566V154OptixCollectKOutputIndexedMergePathDesignTest(unittest.TestCase):
    def test_report_rejects_goal1565_atomic_reset_path(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("reset plus atomic block-count accumulation", text)
        self.assertIn("correct but slower", text)
        self.assertIn("output-indexed merge-path", text)

    def test_report_defines_stable_partition_conditions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("first_rows[i - 1] <= second_rows[j]", text)
        self.assertIn("second_rows[j - 1] < first_rows[i]", text)
        self.assertIn("first-segment rows come before equal second-segment rows", text)
        self.assertIn("lower_bound(second_rows, first_value)", text)
        self.assertIn("upper_bound(first_rows, second_value)", text)

    def test_report_records_external_review_and_caveats(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("boundary partitions where `i = 0` or `j = 0`", text)
        self.assertIn("same `first_value <= second_value` ordering", text)
        self.assertIn("Claude reviewed this design", text)
        self.assertIn("goal1566_claude_output_indexed_merge_path_review_2026-05-08.md", text)

    def test_report_keeps_candidate_diagnostic_only(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Keep production unchanged", text)
        self.assertIn("Do not publish speedup", text)
        self.assertIn("diagnostic-only", text)


if __name__ == "__main__":
    unittest.main()
