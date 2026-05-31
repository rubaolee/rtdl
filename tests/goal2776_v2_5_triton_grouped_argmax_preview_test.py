from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2776_v2_5_grouped_argmax_witness_reduction_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2776_gemini_review_grouped_argmax_witness_reduction_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2776_v2_5_grouped_argmax_witness_reduction_consensus_2026-05-31.md"


class Goal2776V25TritonGroupedArgmaxPreviewTest(unittest.TestCase):
    def test_triton_grouped_argmax_descriptor_is_preview_not_promoted(self):
        descriptor = rt.describe_triton_grouped_argmax_f64()

        self.assertEqual(descriptor["operation"], "grouped_argmax_f64")
        self.assertEqual(descriptor["partner"], "triton")
        self.assertEqual(descriptor["status"], "preview_not_promoted")
        self.assertTrue(descriptor["triton_kernel_available"])
        self.assertEqual(descriptor["tie_break"], "highest_score_then_lowest_item_id")
        self.assertTrue(descriptor["tensor_carrier_compaction_used"])
        self.assertFalse(descriptor["cupy_required"])
        self.assertFalse(descriptor["pytorch_partner_required"])
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_preview_kernel_set_and_support_matrix_include_grouped_argmax(self):
        self.assertIn("grouped_argmax_f64", rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)
        self.assertIn("grouped_argmax_f64", rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertNotIn("grouped_argmax_f64", rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS)

        triton = rt.plan_v2_5_partner_support("grouped_argmax_f64", "triton")
        numba = rt.plan_v2_5_partner_support("grouped_argmax_f64", "numba")
        cupy = rt.plan_v2_5_partner_support("grouped_argmax_f64", "cupy")
        self.assertEqual(triton["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertEqual(numba["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
        self.assertEqual(cupy["status"], rt.V2_5_SUPPORT_STATUS_DESCRIPTOR)

    def test_reference_grouped_argmax_has_deterministic_tie_break(self):
        result = rt.execute_v2_5_partner_continuation_reference(
            "grouped_argmax_f64",
            {
                "group_ids": [0, 0, 1, 1, 1],
                "item_ids": [9, 8, 2, 1, 3],
                "scores": [4.0, 4.0, 7.0, 9.0, 9.0],
                "group_count": 3,
            },
        )

        self.assertEqual(result["outputs"]["group_ids"], [0, 1])
        self.assertEqual(result["outputs"]["item_ids"], [8, 1])
        self.assertEqual(result["outputs"]["scores"], [4.0, 9.0])
        self.assertEqual(result["outputs"]["missing_group_ids"], [2])

    def test_source_uses_triton_argmax_kernels_and_no_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("_triton_grouped_argmax_score_f64_kernel", source)
        self.assertIn("_triton_grouped_argmax_item_i64_kernel", source)
        self.assertIn("tl.atomic_max", source)
        self.assertIn("highest_score_then_lowest_item_id", source)
        self.assertNotIn("RawKernel", source)

    def test_grouped_argmax_matches_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        group_ids = torch.tensor([0, 0, 1, 1, 1], dtype=torch.int64, device="cuda")
        item_ids = torch.tensor([9, 8, 2, 1, 3], dtype=torch.int64, device="cuda")
        scores = torch.tensor([4.0, 4.0, 7.0, 9.0, 9.0], dtype=torch.float64, device="cuda")
        result = rt.run_triton_grouped_argmax_f64(group_ids, item_ids, scores, group_count=3)

        self.assertEqual(result["outputs"]["group_ids"].detach().cpu().tolist(), [0, 1])
        self.assertEqual(result["outputs"]["item_ids"].detach().cpu().tolist(), [8, 1])
        self.assertEqual(result["outputs"]["scores"].detach().cpu().tolist(), [4.0, 9.0])
        self.assertEqual(result["outputs"]["missing_group_ids"].detach().cpu().tolist(), [2])

    def test_report_records_goal2776_boundary(self):
        report = REPORT.read_text()

        self.assertIn("grouped_argmax_f64", report)
        self.assertIn("highest-score", report)
        self.assertIn("not a public speedup claim", report)
        self.assertIn("goal2776_triton_grouped_argmax_pod_69_30_85_171_2026-05-31.json", report)

    def test_review_and_consensus_record_acceptance_boundary(self):
        review = REVIEW.read_text()
        consensus = CONSENSUS.read_text()

        self.assertIn("Verdict: accept", review)
        self.assertIn("Goal2776 is accepted for the internal v2.5 preview lane", consensus)
        self.assertIn("does not authorize", consensus)
        self.assertIn("true-zero-copy claims", consensus)


if __name__ == "__main__":
    unittest.main()
