from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2663V25TritonSegmentedSumTest(unittest.TestCase):
    def test_triton_segmented_descriptors_are_safe_without_runtime_import(self):
        count_descriptor = rt.describe_triton_segmented_count_i64()
        sum_descriptor = rt.describe_triton_segmented_sum_f64()

        self.assertEqual(count_descriptor["operation"], "segmented_count_i64")
        self.assertEqual(count_descriptor["partner"], "triton")
        self.assertEqual(count_descriptor["status"], "preview_not_promoted")
        self.assertFalse(count_descriptor["raw_kernel_required"])
        self.assertFalse(count_descriptor["replaces_rt_traversal"])
        self.assertFalse(count_descriptor["promoted_performance_path"])
        self.assertEqual(sum_descriptor["operation"], "segmented_sum_f64")
        self.assertEqual(sum_descriptor["partner"], "triton")
        self.assertEqual(sum_descriptor["status"], "preview_not_promoted")
        self.assertFalse(sum_descriptor["raw_kernel_required"])
        self.assertFalse(sum_descriptor["replaces_rt_traversal"])
        self.assertFalse(sum_descriptor["promoted_performance_path"])
        self.assertIn("run_triton_segmented_count_i64", rt.__all__)
        self.assertIn("run_triton_segmented_sum_f64", rt.__all__)

    def test_triton_module_is_lazy_import_and_records_no_rawkernel(self):
        source = (ROOT / "src/rtdsl/triton_partner_continuation.py").read_text()

        self.assertIn("@__import__(\"triton\").jit", source)
        self.assertIn("tl.atomic_add", source)
        self.assertIn("group_ids must be in [0, group_count)", source)
        self.assertIn("TRITON_SEGMENTED_COUNT_I64_OPERATION", source)
        self.assertNotIn("RawKernel", source)
        self.assertNotIn("raydb", source.lower())
        self.assertNotIn("dbscan", source.lower())
        self.assertNotIn("barnes", source.lower())

    def test_triton_availability_probe_is_boolean(self):
        self.assertIsInstance(rt.triton_partner_available(), bool)

    def test_triton_segmented_count_matches_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        group_ids = torch.tensor([0, 2, 2, 1, 0], dtype=torch.int64, device="cuda")
        result = rt.run_triton_segmented_count_i64(group_ids, group_count=4)
        reference = rt.execute_v2_5_partner_continuation_reference(
            "segmented_count_i64",
            {"group_ids": [0, 2, 2, 1, 0], "group_count": 4},
        )

        self.assertEqual(result["status"], "preview_not_promoted")
        self.assertFalse(result["promoted_performance_path"])
        self.assertEqual(result["phase_timing"]["validation"]["status"], "accept")
        self.assertEqual(result["outputs"]["counts"].detach().cpu().tolist(), reference["outputs"]["counts"])

    def test_triton_segmented_sum_matches_reference_when_cuda_available(self):
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton validation")

        import torch

        group_ids = torch.tensor([0, 2, 2, 1, 0], dtype=torch.int64, device="cuda")
        values = torch.tensor([1.0, 2.5, 3.5, 4.0, 6.0], dtype=torch.float64, device="cuda")
        result = rt.run_triton_segmented_sum_f64(group_ids, values, group_count=4)
        reference = rt.execute_v2_5_partner_continuation_reference(
            "segmented_sum_f64",
            {"group_ids": [0, 2, 2, 1, 0], "values": [1.0, 2.5, 3.5, 4.0, 6.0], "group_count": 4},
        )

        self.assertEqual(result["status"], "preview_not_promoted")
        self.assertFalse(result["promoted_performance_path"])
        self.assertEqual(result["phase_timing"]["validation"]["status"], "accept")
        self.assertEqual(result["outputs"]["sums"].detach().cpu().tolist(), reference["outputs"]["sums"])

    def test_docs_record_goal2663_pod_gate(self):
        report = (ROOT / "docs/reports/goal2663_v2_5_triton_segmented_sum_preview_2026-05-27.md").read_text()
        count_report = (
            ROOT / "docs/reports/goal2664_v2_5_triton_segmented_count_preview_2026-05-27.md"
        ).read_text()

        self.assertIn("pod validation required", report)
        self.assertIn("preview_not_promoted", report)
        self.assertIn("no public speedup claim", report)
        self.assertIn("segmented_count_i64", count_report)
        self.assertIn("pod validation required", count_report)
        self.assertIn("no public speedup claim", count_report)


if __name__ == "__main__":
    unittest.main()
