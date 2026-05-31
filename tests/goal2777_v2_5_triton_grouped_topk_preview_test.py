from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2777_gemini_review_grouped_topk_ranked_summary_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_consensus_2026-05-31.md"


class Goal2777V25TritonGroupedTopKPreviewTest(unittest.TestCase):
    def test_triton_grouped_topk_descriptor_is_preview_not_promoted(self):
        descriptor = rt.describe_triton_grouped_topk_f64()

        self.assertEqual(descriptor["operation"], "grouped_topk_f64")
        self.assertEqual(descriptor["partner"], "triton")
        self.assertEqual(descriptor["status"], "preview_not_promoted")
        self.assertTrue(descriptor["triton_kernel_available"])
        self.assertEqual(descriptor["tie_break"], "lowest_score_then_lowest_item_id")
        self.assertEqual(descriptor["duplicate_item_policy"], "lowest_score_per_group_item")
        self.assertEqual(descriptor["max_k"], 64)
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_preview_kernel_set_and_support_matrix_include_grouped_topk(self):
        self.assertIn("grouped_topk_f64", rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)
        self.assertIn("grouped_topk_f64", rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertNotIn("grouped_topk_f64", rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS)

        triton = rt.plan_v2_5_partner_support("grouped_topk_f64", "triton")
        numba = rt.plan_v2_5_partner_support("grouped_topk_f64", "numba")
        cupy = rt.plan_v2_5_partner_support("grouped_topk_f64", "cupy")
        self.assertEqual(triton["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertEqual(numba["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
        self.assertEqual(cupy["status"], rt.V2_5_SUPPORT_STATUS_DESCRIPTOR)

    def test_reference_grouped_topk_is_deterministic_and_distinct_by_item(self):
        result = rt.execute_v2_5_partner_continuation_reference(
            "grouped_topk_f64",
            {
                "group_ids": [0, 0, 0, 1, 1, 1, 1],
                "item_ids": [9, 8, 8, 2, 1, 3, 4],
                "scores": [4.0, 4.0, 3.5, 7.0, 9.0, 9.0, 6.0],
                "group_count": 3,
                "k": 2,
            },
        )

        self.assertEqual(result["outputs"]["group_ids"], [0, 0, 1, 1])
        self.assertEqual(result["outputs"]["item_ids"], [8, 9, 4, 2])
        self.assertEqual(result["outputs"]["scores"], [3.5, 4.0, 6.0, 7.0])
        self.assertEqual(result["outputs"]["ranks"], [1, 2, 1, 2])
        self.assertEqual(result["outputs"]["row_offsets"], [0, 2, 4, 4])
        self.assertEqual(result["outputs"]["missing_group_ids"], [2])

    def test_source_uses_triton_topk_kernels_and_no_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("_triton_grouped_topk_score_f64_kernel", source)
        self.assertIn("_triton_grouped_topk_item_i64_kernel", source)
        self.assertIn("_triton_grouped_topk_store_rank_kernel", source)
        self.assertIn("tl.atomic_min", source)
        self.assertIn("lowest_score_then_lowest_item_id", source)
        self.assertNotIn("RawKernel", source)

    def test_grouped_topk_matches_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        group_ids = torch.tensor([0, 0, 0, 1, 1, 1, 1], dtype=torch.int64, device="cuda")
        item_ids = torch.tensor([9, 8, 8, 2, 1, 3, 4], dtype=torch.int64, device="cuda")
        scores = torch.tensor([4.0, 4.0, 3.5, 7.0, 9.0, 9.0, 6.0], dtype=torch.float64, device="cuda")
        result = rt.run_triton_grouped_topk_f64(group_ids, item_ids, scores, group_count=3, k=2)

        self.assertEqual(result["outputs"]["group_ids"].detach().cpu().tolist(), [0, 0, 1, 1])
        self.assertEqual(result["outputs"]["item_ids"].detach().cpu().tolist(), [8, 9, 4, 2])
        self.assertEqual(result["outputs"]["scores"].detach().cpu().tolist(), [3.5, 4.0, 6.0, 7.0])
        self.assertEqual(result["outputs"]["ranks"].detach().cpu().tolist(), [1, 2, 1, 2])
        self.assertEqual(result["outputs"]["row_offsets"].detach().cpu().tolist(), [0, 2, 4, 4])
        self.assertEqual(result["outputs"]["missing_group_ids"].detach().cpu().tolist(), [2])

    def test_report_records_goal2777_boundary(self):
        report = REPORT.read_text()

        self.assertIn("grouped_topk_f64", report)
        self.assertIn("RTNN", report)
        self.assertIn("not a public speedup claim", report)
        self.assertIn("goal2777_triton_grouped_topk_pod_69_30_85_171_2026-05-31.json", report)

    def test_review_and_consensus_record_acceptance_boundary(self):
        review = REVIEW.read_text()
        consensus = CONSENSUS.read_text()

        self.assertIn("Overall Verdict: accept-with-boundary", review)
        self.assertIn("Goal2777 is accepted for the internal v2.5 preview lane", consensus)
        self.assertIn("does not authorize", consensus)
        self.assertIn("RTNN paper reproduction claims", consensus)


if __name__ == "__main__":
    unittest.main()
