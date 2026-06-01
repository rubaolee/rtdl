from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2778_v2_5_grouped_vector_sum_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2778_gemini_review_grouped_vector_sum_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2778_v2_5_grouped_vector_sum_consensus_2026-05-31.md"


class Goal2778V25TritonGroupedVectorSumPreviewTest(unittest.TestCase):
    def test_triton_grouped_vector_sum_descriptor_is_preview_not_promoted(self):
        descriptor = rt.describe_triton_grouped_vector_sum_f64x2()

        self.assertEqual(descriptor["operation"], "grouped_vector_sum_f64x2")
        self.assertEqual(descriptor["partner"], "triton")
        self.assertEqual(descriptor["status"], "preview_not_promoted")
        self.assertTrue(descriptor["triton_kernel_available"])
        self.assertEqual(descriptor["vector_width"], 2)
        self.assertEqual(descriptor["component_contract"], "paired_float64_components")
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_preview_kernel_set_and_support_matrix_include_grouped_vector_sum(self):
        self.assertIn("grouped_vector_sum_f64x2", rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)
        self.assertIn("grouped_vector_sum_f64x2", rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertNotIn("grouped_vector_sum_f64x2", rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS)

        triton = rt.plan_v2_5_partner_support("grouped_vector_sum_f64x2", "triton")
        numba = rt.plan_v2_5_partner_support("grouped_vector_sum_f64x2", "numba")
        cupy = rt.plan_v2_5_partner_support("grouped_vector_sum_f64x2", "cupy")
        self.assertEqual(triton["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertEqual(numba["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
        self.assertEqual(cupy["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)

    def test_reference_grouped_vector_sum_is_componentwise(self):
        result = rt.execute_v2_5_partner_continuation_reference(
            "grouped_vector_sum_f64x2",
            {
                "group_ids": [0, 2, 2, 1, 0],
                "values_x": [1.0, 2.5, 3.5, 4.0, 6.0],
                "values_y": [0.5, -1.0, 2.0, 3.0, -0.5],
                "group_count": 4,
            },
        )

        self.assertEqual(result["outputs"]["sum_x"], [7.0, 4.0, 6.0, 0.0])
        self.assertEqual(result["outputs"]["sum_y"], [0.0, 3.0, 1.0, 0.0])

    def test_source_uses_triton_vector_sum_kernel_and_no_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("_triton_grouped_vector_sum_f64x2_kernel", source)
        self.assertIn("tl.atomic_add(output_x", source)
        self.assertIn("tl.atomic_add(output_y", source)
        self.assertIn("paired_float64_components", source)
        self.assertNotIn("RawKernel", source)

    def test_grouped_vector_sum_matches_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        group_ids = torch.tensor([0, 2, 2, 1, 0], dtype=torch.int64, device="cuda")
        values_x = torch.tensor([1.0, 2.5, 3.5, 4.0, 6.0], dtype=torch.float64, device="cuda")
        values_y = torch.tensor([0.5, -1.0, 2.0, 3.0, -0.5], dtype=torch.float64, device="cuda")
        result = rt.run_triton_grouped_vector_sum_f64x2(group_ids, values_x, values_y, group_count=4)

        self.assertEqual(result["outputs"]["sum_x"].detach().cpu().tolist(), [7.0, 4.0, 6.0, 0.0])
        self.assertEqual(result["outputs"]["sum_y"].detach().cpu().tolist(), [0.0, 3.0, 1.0, 0.0])

    def test_report_records_goal2778_boundary(self):
        report = REPORT.read_text()

        self.assertIn("grouped_vector_sum_f64x2", report)
        self.assertIn("Barnes-Hut", report)
        self.assertIn("not a public speedup claim", report)
        self.assertIn("goal2778_triton_grouped_vector_sum_pod_69_30_85_171_2026-05-31.json", report)

    def test_review_and_consensus_record_acceptance_boundary(self):
        review = REVIEW.read_text()
        consensus = CONSENSUS.read_text()

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("Goal2778 is accepted for the internal v2.5 preview lane", consensus)
        self.assertIn("does not authorize", consensus)
        self.assertIn("Barnes-Hut force-accuracy claims", consensus)


if __name__ == "__main__":
    unittest.main()
