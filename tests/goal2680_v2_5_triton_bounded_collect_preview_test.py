from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2680V25TritonBoundedCollectPreviewTest(unittest.TestCase):
    def test_triton_bounded_collect_descriptor_is_preview_not_promoted(self):
        descriptor = rt.describe_triton_bounded_collect_finalize_i64()

        self.assertEqual(descriptor["operation"], "bounded_collect_finalize_i64")
        self.assertEqual(descriptor["partner"], "triton")
        self.assertEqual(descriptor["status"], "preview_not_promoted")
        self.assertTrue(descriptor["triton_kernel_available"])
        self.assertEqual(descriptor["failure_mode"], "fail_closed_overflow")
        self.assertEqual(descriptor["within_group_order"], "unspecified_nonsemantic")
        self.assertTrue(descriptor["tensor_carrier_prefix_sum_used"])
        self.assertFalse(descriptor["cupy_required"])
        self.assertFalse(descriptor["pytorch_partner_required"])
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_bounded_collect_has_triton_preview_while_hit_stream_preview_is_cupy_scoped(self):
        self.assertIn("bounded_collect_finalize_i64", rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertNotIn("hit_stream_grouped_ray_id_primitive_i64", rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertIn("hit_stream_grouped_ray_id_primitive_i64", rt.V2_5_CUPY_PREVIEW_OPERATIONS)
        self.assertEqual(rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS, ())

    def test_source_uses_triton_count_prefix_sum_scatter_and_no_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("_triton_segmented_count_i64_kernel", source)
        self.assertIn("torch.cumsum", source)
        self.assertIn("_triton_bounded_collect_scatter_i64_kernel", source)
        self.assertIn("fail_closed_overflow", source)
        self.assertNotIn("RawKernel", source)

    def test_bounded_collect_matches_reference_sets_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        group_ids = torch.tensor([0, 1, 1, 2], dtype=torch.int64, device="cuda")
        item_ids = torch.tensor([10, 20, 21, 30], dtype=torch.int64, device="cuda")
        result = rt.run_triton_bounded_collect_finalize_i64(group_ids, item_ids, group_count=3, k=2)

        self.assertEqual(result["outputs"]["row_offsets"].detach().cpu().tolist(), [0, 1, 3, 4])
        out_groups = result["outputs"]["group_ids"].detach().cpu().tolist()
        out_items = result["outputs"]["item_ids"].detach().cpu().tolist()
        rows_by_group = {
            group: sorted(item for out_group, item in zip(out_groups, out_items) if out_group == group)
            for group in range(3)
        }
        self.assertEqual(rows_by_group, {0: [10], 1: [20, 21], 2: [30]})

        with self.assertRaises(rt.PartnerContinuationOverflowError):
            rt.run_triton_bounded_collect_finalize_i64(group_ids, item_ids, group_count=3, k=1)


if __name__ == "__main__":
    unittest.main()
