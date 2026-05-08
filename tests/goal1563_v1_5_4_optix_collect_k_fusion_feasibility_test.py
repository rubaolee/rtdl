import unittest
from pathlib import Path


REPORT = Path("docs/reports/goal1563_v1_5_4_optix_collect_k_fusion_feasibility_2026-05-08.md")
CORE_CPP = Path("src/native/optix/rtdl_optix_core.cpp")


class Goal1563V154OptixCollectKFusionFeasibilityTest(unittest.TestCase):
    def test_report_records_naive_fusion_hazard(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Do not implement a naive", text)
        self.assertIn("fully\nmaterialized, globally ordered merged row buffer", text)
        self.assertIn("CUDA has no grid-wide synchronization inside a\nnormal kernel", text)
        self.assertIn("derives predecessor rows from input segments", text)

    def test_report_names_current_four_kernel_block(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_mark_counts_level_counts", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_prefix_offsets_level", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_compact_level_derived", text)

    def test_report_records_required_correctness_cases(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Boundary rows", text)
        self.assertIn("Equal-valued candidates", text)
        self.assertIn("Threads must be assigned by input row", text)
        self.assertIn("Partial final blocks", text)
        self.assertIn("Skewed or short pairs", text)
        self.assertIn("goal1563_claude_fusion_feasibility_review_2026-05-08.md", text)

    def test_source_still_uses_separate_materialize_and_mark_kernels(self) -> None:
        source = CORE_CPP.read_text(encoding="utf-8")
        self.assertIn("collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived", source)
        self.assertIn("collect_k_bounded_i64_row_width2_final_mark_counts_level_counts", source)
        self.assertIn("pair_merged_rows[(local_index - 1) * 2]", source)


if __name__ == "__main__":
    unittest.main()
