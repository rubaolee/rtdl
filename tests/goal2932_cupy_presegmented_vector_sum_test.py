from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal2932_cupy_presegmented_vector_sum_partner_2026-06-01.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2932_cupy_presegmented_vector_sum_pod" / "goal2932_cupy_vector_sum_8192x16.json"


class Goal2932CupyPresegmentedVectorSumTest(unittest.TestCase):
    def test_cupy_presegmented_rawkernel_path_is_generic(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def _cupy_grouped_vector_sum_2d_by_offsets", source)
        self.assertIn("rtdl_cupy_grouped_vector_sum_offsets_f64x2", source)
        self.assertIn('"v2_5_cupy_rawkernel_used"', source)
        self.assertIn('"v2_5_cupy_presegmented_offsets_used"', source)
        self.assertIn('"not_called_partner_continuation_only"', source)

    def test_support_and_conformance_matrices_index_cupy_preview(self) -> None:
        support = rt.plan_v2_5_partner_support("grouped_vector_sum_f64x2", "cupy")
        conformance = rt.plan_v2_5_partner_conformance("grouped_vector_sum_f64x2", "cupy")

        self.assertIn("grouped_vector_sum_f64x2", rt.V2_5_CUPY_PREVIEW_OPERATIONS)
        self.assertEqual(rt.V2_5_SUPPORT_STATUS_PREVIEW, support["status"])
        self.assertEqual(rt.V2_5_CONFORMANCE_STATUS_POD_RUNTIME, conformance["conformance_status"])
        self.assertEqual("Goal2932", conformance["evidence_goal"])
        self.assertFalse(conformance["public_speedup_claim_authorized"])
        self.assertFalse(conformance["true_zero_copy_claim_authorized"])

    def test_cupy_rawkernel_matches_expected_when_cuda_available(self) -> None:
        try:
            import cupy
        except ImportError:  # pragma: no cover
            self.skipTest("cupy is not installed")
        if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
            self.skipTest("CuPy CUDA is not available")

        columns = {
            "group_ids": cupy.asarray([0, 0, 1, 2, 2, 2], dtype=cupy.int64),
            "row_offsets": cupy.asarray([0, 2, 3, 6], dtype=cupy.int64),
            "values_x": cupy.asarray([1.5, 2.5, -1.0, 4.0, 5.0, -2.0], dtype=cupy.float64),
            "values_y": cupy.asarray([10.0, -4.0, 3.0, 0.25, 0.75, 1.0], dtype=cupy.float64),
        }
        result = rt.grouped_vector_sum_2d_partner_columns(
            columns,
            group_count=3,
            partner="cupy",
            return_metadata=True,
        )

        self.assertEqual(cupy.asnumpy(result["columns"]["sum_x"]).tolist(), [4.0, -1.0, 7.0])
        self.assertEqual(cupy.asnumpy(result["columns"]["sum_y"]).tolist(), [6.0, 3.0, 2.0])
        metadata = result["metadata"]
        self.assertTrue(metadata["v2_5_cupy_rawkernel_used"])
        self.assertTrue(metadata["v2_5_cupy_presegmented_offsets_used"])
        self.assertEqual("cupy_grouped_vector_sum_offsets_f64x2_kernel", metadata["v2_5_cupy_adapter_kernel"])
        self.assertFalse(metadata["v2_5_cupy_global_atomic_add_used"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

    def test_pod_report_records_result_and_boundaries(self) -> None:
        if not REPORT.exists() or not ARTIFACT.exists():
            self.skipTest("Goal2932 pod artifact has not been recorded yet")
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual("pass", artifact["status"])
        self.assertTrue(artifact["matches"]["cupy_offsets_matches_torch"])
        self.assertTrue(artifact["metadata"]["cupy_offsets_rawkernel"]["v2_5_cupy_rawkernel_used"])
        self.assertFalse(artifact["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["v2_5_release_authorized"])
        self.assertIn("Goal2932", report)
        self.assertIn("generic CuPy RawKernel", report)
        self.assertIn("does not authorize v2.5 release", report)


if __name__ == "__main__":
    unittest.main()
