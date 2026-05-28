from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2678V25TritonCompactMaskPreviewTest(unittest.TestCase):
    def test_triton_compact_descriptor_is_preview_not_promoted(self):
        descriptor = rt.describe_triton_compact_mask_i64()

        self.assertEqual(descriptor["operation"], "compact_mask_i64")
        self.assertEqual(descriptor["partner"], "triton")
        self.assertEqual(descriptor["status"], "preview_not_promoted")
        self.assertTrue(descriptor["triton_kernel_available"])
        self.assertTrue(descriptor["tensor_carrier_prefix_sum_used"])
        self.assertFalse(descriptor["cupy_required"])
        self.assertFalse(descriptor["pytorch_partner_required"])
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_preview_kernel_set_includes_compact_mask(self):
        self.assertIn("compact_mask_i64", rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertNotIn("compact_mask_i64", rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS)

    def test_source_uses_triton_cumsum_and_no_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("tl.cumsum", source)
        self.assertIn("_triton_compact_count_blocks_i64_kernel", source)
        self.assertIn("_triton_compact_scatter_i64_kernel", source)
        self.assertIn("tensor_carrier_prefix_sum_used", source)
        self.assertNotIn("RawKernel", source)

    def test_compact_matches_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        values = torch.tensor([10, 20, 30, 40], dtype=torch.int64, device="cuda")
        mask = torch.tensor([False, True, True, False], dtype=torch.bool, device="cuda")
        result = rt.run_triton_compact_mask_i64(values, mask)

        self.assertEqual(result["outputs"]["values"].detach().cpu().tolist(), [20, 30])
        self.assertEqual(result["outputs"]["original_indices"].detach().cpu().tolist(), [1, 2])


if __name__ == "__main__":
    unittest.main()
