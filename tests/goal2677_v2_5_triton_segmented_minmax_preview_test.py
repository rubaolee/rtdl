from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2677V25TritonSegmentedMinMaxPreviewTest(unittest.TestCase):
    def test_triton_segmented_minmax_descriptors_are_preview_not_promoted(self):
        min_descriptor = rt.describe_triton_segmented_min_f64()
        max_descriptor = rt.describe_triton_segmented_max_f64()

        self.assertEqual(min_descriptor["operation"], "segmented_min_f64")
        self.assertEqual(max_descriptor["operation"], "segmented_max_f64")
        for descriptor in (min_descriptor, max_descriptor):
            self.assertEqual(descriptor["partner"], "triton")
            self.assertEqual(descriptor["status"], "preview_not_promoted")
            self.assertTrue(descriptor["triton_kernel_available"])
            self.assertTrue(descriptor["tensor_carrier_compaction_used"])
            self.assertFalse(descriptor["cupy_required"])
            self.assertFalse(descriptor["pytorch_partner_required"])
            self.assertFalse(descriptor["promoted_performance_path"])
            self.assertFalse(descriptor["replaces_rt_traversal"])

    def test_preview_kernel_set_includes_minmax(self):
        self.assertEqual(
            rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS,
            (
                "segmented_count_i64",
                "segmented_sum_f64",
                "grouped_vector_sum_f64x2",
                "segmented_min_f64",
                "segmented_max_f64",
                "compact_mask_i64",
                "edge_list_components_i64",
                "grouped_argmin_f64",
                "grouped_argmax_f64",
                "grouped_topk_f64",
                "bounded_collect_finalize_i64",
            ),
        )
        self.assertNotIn("segmented_min_f64", rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS)
        self.assertNotIn("segmented_max_f64", rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS)

    def test_source_uses_triton_atomic_minmax_not_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("tl.atomic_min", source)
        self.assertIn("tl.atomic_max", source)
        self.assertIn("tensor_carrier_compaction_used", source)
        self.assertNotIn("RawKernel", source)

    def test_minmax_match_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        group_ids = torch.tensor([0, 2, 2, 1, 0], dtype=torch.int64, device="cuda")
        values = torch.tensor([1.0, 2.5, 3.5, 4.0, 6.0], dtype=torch.float64, device="cuda")
        min_result = rt.run_triton_segmented_min_f64(group_ids, values, group_count=4)
        max_result = rt.run_triton_segmented_max_f64(group_ids, values, group_count=4)
        min_reference = rt.execute_v2_5_partner_continuation_reference(
            "segmented_min_f64",
            {"group_ids": [0, 2, 2, 1, 0], "values": [1.0, 2.5, 3.5, 4.0, 6.0], "group_count": 4},
        )
        max_reference = rt.execute_v2_5_partner_continuation_reference(
            "segmented_max_f64",
            {"group_ids": [0, 2, 2, 1, 0], "values": [1.0, 2.5, 3.5, 4.0, 6.0], "group_count": 4},
        )

        self.assertEqual(min_result["outputs"]["group_ids"].detach().cpu().tolist(), min_reference["outputs"]["group_ids"])
        self.assertEqual(min_result["outputs"]["mins"].detach().cpu().tolist(), min_reference["outputs"]["mins"])
        self.assertEqual(
            min_result["outputs"]["missing_group_ids"].detach().cpu().tolist(),
            min_reference["outputs"]["missing_group_ids"],
        )
        self.assertEqual(max_result["outputs"]["group_ids"].detach().cpu().tolist(), max_reference["outputs"]["group_ids"])
        self.assertEqual(max_result["outputs"]["maxes"].detach().cpu().tolist(), max_reference["outputs"]["maxes"])
        self.assertEqual(
            max_result["outputs"]["missing_group_ids"].detach().cpu().tolist(),
            max_reference["outputs"]["missing_group_ids"],
        )


if __name__ == "__main__":
    unittest.main()
