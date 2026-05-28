from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2679V25TritonGroupedArgminPreviewTest(unittest.TestCase):
    def test_triton_grouped_argmin_descriptor_is_preview_not_promoted(self):
        descriptor = rt.describe_triton_grouped_argmin_f64()

        self.assertEqual(descriptor["operation"], "grouped_argmin_f64")
        self.assertEqual(descriptor["partner"], "triton")
        self.assertEqual(descriptor["status"], "preview_not_promoted")
        self.assertTrue(descriptor["triton_kernel_available"])
        self.assertEqual(descriptor["tie_break"], "lowest_score_then_lowest_item_id")
        self.assertTrue(descriptor["tensor_carrier_compaction_used"])
        self.assertFalse(descriptor["cupy_required"])
        self.assertFalse(descriptor["pytorch_partner_required"])
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_preview_kernel_set_includes_grouped_argmin(self):
        self.assertIn("grouped_argmin_f64", rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertNotIn("grouped_argmin_f64", rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS)

    def test_source_uses_triton_argmin_kernels_and_no_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("_triton_grouped_argmin_score_f64_kernel", source)
        self.assertIn("_triton_grouped_argmin_item_i64_kernel", source)
        self.assertIn("tl.atomic_min", source)
        self.assertIn("lowest_score_then_lowest_item_id", source)
        self.assertNotIn("RawKernel", source)

    def test_grouped_argmin_matches_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        group_ids = torch.tensor([0, 0, 1, 1, 1], dtype=torch.int64, device="cuda")
        item_ids = torch.tensor([9, 8, 2, 1, 3], dtype=torch.int64, device="cuda")
        scores = torch.tensor([4.0, 4.0, 7.0, 5.0, 5.0], dtype=torch.float64, device="cuda")
        result = rt.run_triton_grouped_argmin_f64(group_ids, item_ids, scores, group_count=3)

        self.assertEqual(result["outputs"]["group_ids"].detach().cpu().tolist(), [0, 1])
        self.assertEqual(result["outputs"]["item_ids"].detach().cpu().tolist(), [8, 1])
        self.assertEqual(result["outputs"]["scores"].detach().cpu().tolist(), [4.0, 5.0])
        self.assertEqual(result["outputs"]["missing_group_ids"].detach().cpu().tolist(), [2])


if __name__ == "__main__":
    unittest.main()
