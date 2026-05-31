from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2779_gemini_review_edge_list_components_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2779_v2_5_edge_list_components_consensus_2026-05-31.md"


class Goal2779V25TritonEdgeListComponentsPreviewTest(unittest.TestCase):
    def test_triton_edge_list_components_descriptor_is_preview_not_promoted(self):
        descriptor = rt.describe_triton_edge_list_components_i64()

        self.assertEqual(descriptor["operation"], "edge_list_components_i64")
        self.assertEqual(descriptor["partner"], "triton")
        self.assertEqual(descriptor["status"], "preview_not_promoted")
        self.assertTrue(descriptor["triton_kernel_available"])
        self.assertEqual(descriptor["algorithm"], "fixed_iteration_min_label_propagation")
        self.assertEqual(descriptor["component_label"], "smallest_node_id_in_component")
        self.assertFalse(descriptor["promoted_performance_path"])

    def test_preview_kernel_set_and_support_matrix_include_edge_components(self):
        self.assertIn("edge_list_components_i64", rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)
        self.assertIn("edge_list_components_i64", rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertNotIn("edge_list_components_i64", rt.V2_5_PARTNER_REFERENCE_ONLY_OPERATIONS)

        triton = rt.plan_v2_5_partner_support("edge_list_components_i64", "triton")
        numba = rt.plan_v2_5_partner_support("edge_list_components_i64", "numba")
        cupy = rt.plan_v2_5_partner_support("edge_list_components_i64", "cupy")
        self.assertEqual(triton["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertEqual(numba["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
        self.assertEqual(cupy["status"], rt.V2_5_SUPPORT_STATUS_DESCRIPTOR)

    def test_reference_components_label_by_smallest_node_id(self):
        result = rt.execute_v2_5_partner_continuation_reference(
            "edge_list_components_i64",
            {
                "source_ids": [0, 1, 3, 6],
                "target_ids": [1, 2, 4, 7],
                "node_count": 8,
                "max_iterations": 8,
            },
        )

        self.assertEqual(result["outputs"]["component_ids"], [0, 0, 0, 3, 3, 5, 6, 6])

    def test_source_uses_triton_component_kernels_and_no_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("_triton_edge_list_component_relax_i64_kernel", source)
        self.assertIn("_triton_edge_list_component_compress_i64_kernel", source)
        self.assertIn("tl.atomic_min(component_ids", source)
        self.assertIn("fixed_iteration_min_label_propagation", source)
        self.assertNotIn("RawKernel", source)

    def test_edge_list_components_match_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        source_ids = torch.tensor([0, 1, 3, 6], dtype=torch.int64, device="cuda")
        target_ids = torch.tensor([1, 2, 4, 7], dtype=torch.int64, device="cuda")
        result = rt.run_triton_edge_list_components_i64(
            source_ids,
            target_ids,
            node_count=8,
            max_iterations=8,
        )

        self.assertEqual(result["outputs"]["component_ids"].detach().cpu().tolist(), [0, 0, 0, 3, 3, 5, 6, 6])

    def test_report_records_goal2779_boundary(self):
        report = REPORT.read_text()

        self.assertIn("edge_list_components_i64", report)
        self.assertIn("DBSCAN", report)
        self.assertIn("not a public speedup claim", report)
        self.assertIn("goal2779_triton_edge_list_components_pod_69_30_85_171_2026-05-31.json", report)

    def test_review_and_consensus_record_acceptance_boundary(self):
        review = REVIEW.read_text()
        consensus = CONSENSUS.read_text()

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("Goal2779 is accepted for the internal v2.5 preview lane", consensus)
        self.assertIn("does not authorize", consensus)
        self.assertIn("DBSCAN cluster-quality claims", consensus)


if __name__ == "__main__":
    unittest.main()
