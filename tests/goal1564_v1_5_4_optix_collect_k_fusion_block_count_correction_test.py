import unittest
from pathlib import Path


REPORT = Path("docs/reports/goal1564_v1_5_4_optix_collect_k_fusion_block_count_correction_2026-05-08.md")
CLAUDE = Path("docs/reports/goal1564_claude_fusion_block_count_correction_review_2026-05-08.md")
CORE_CPP = Path("src/native/optix/rtdl_optix_core.cpp")


class Goal1564V154OptixCollectKFusionBlockCountCorrectionTest(unittest.TestCase):
    def test_report_rejects_input_block_count_shortcut(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("input-row-owned fused kernel cannot reuse the old shared-memory", text)
        self.assertIn("structural\nownership mismatch", text)
        self.assertIn("Do not implement the fused diagnostic as", text)

    def test_report_selects_atomic_reset_diagnostic_shape(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("marks[output_index]", text)
        self.assertIn("atomicAdd(&block_counts[output_index / blockDim.x], 1)", text)
        self.assertIn("cuMemsetD32Async(marks", text)
        self.assertIn("cuMemsetD32Async(block_counts", text)
        self.assertIn("reset calls are part of the diagnostic cost", text)

    def test_external_review_is_saved(self) -> None:
        self.assertTrue(CLAUDE.exists())
        text = CLAUDE.read_text(encoding="utf-8")
        self.assertIn("Real additional caveat", text)
        self.assertIn("atomicAdd", text)

    def test_current_compact_contract_uses_output_position_marks(self) -> None:
        source = CORE_CPP.read_text(encoding="utf-8")
        self.assertIn("const size_t global_index = blockIdx.x * blockDim.x + threadIdx.x;", source)
        self.assertIn("const uint32_t mark = marks[global_index];", source)
        self.assertIn("block_counts[blockIdx.x] = shared_counts[0];", source)


if __name__ == "__main__":
    unittest.main()
