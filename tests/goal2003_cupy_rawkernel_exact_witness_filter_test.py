from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal2003_cupy_rawkernel_exact_witness_filter_2026-05-14.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2003_pod_smoke" / "segment_polygon_cupy_rawkernel_hitcount_perf.json"


class Goal2003CuPyRawKernelExactWitnessFilterTest(unittest.TestCase):
    def test_cupy_rawkernel_filter_is_generic_partner_side_filter(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("_CUPY_SEGMENT_TRIANGLE_EXACT_WITNESS_FILTER_KERNEL", source)
        self.assertIn("cupy.RawKernel", source)
        self.assertIn("segment_triangle_exact_witness_filter_2d", source)
        self.assertIn("cupy_rawkernel_segment_triangle_filter_from_generic_witness_candidates", source)
        self.assertIn("partner_gpu_unique_pair_counts_from_cupy_exact_filter", source)
        self.assertIn("partner_group_count_unique_pairs_by_key", source)
        self.assertIn('"app_exact_filter_device_materialization": True', source)

    def test_torch_and_fake_runtime_host_boundary_remains_explicit(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("partner_columns_from_host_exact_filter", source)
        self.assertIn('"app_exact_filter_device_materialization": False', source)
        self.assertIn('"whole_app_true_zero_copy_authorized": whole_app_true_zero_copy_authorized', source)

    def test_report_records_pod_evidence_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("NVIDIA RTX A5000", report)
        self.assertIn("whole_app_true_zero_copy_authorized: true", report)
        self.assertIn("v2_0_release_authorized: false", report)
        self.assertIn("RTDL native should produce generic", report)
        self.assertIn("partner adapters provide reusable GPU-side exact filters", report)

    def test_pod_artifact_has_exact_counts_and_speedups(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], "Goal2003")
        self.assertIn("NVIDIA RTX A5000", artifact["gpu"])
        self.assertEqual(len(artifact["results"]), 3)
        for result in artifact["results"]:
            with self.subTest(count=result["count"]):
                self.assertEqual(result["status"], "pass")
                self.assertTrue(result["v2_cupy"]["all_one"])
                metadata = result["v2_cupy"]["metadata"]
                self.assertEqual(
                    metadata["app_exact_filter"],
                    "cupy_rawkernel_segment_triangle_filter_from_generic_witness_candidates",
                )
                self.assertFalse(metadata["app_count_host_materialization"])
                self.assertTrue(metadata["app_exact_filter_device_materialization"])
                self.assertTrue(metadata["whole_app_true_zero_copy_authorized"])
                self.assertFalse(metadata["v2_0_release_authorized"])
                if result["count"] == 256:
                    self.assertGreater(result["v2_cupy"]["ratio_vs_v1_8_median"], 1.0)
                else:
                    self.assertLess(result["v2_cupy"]["ratio_vs_v1_8_median"], 1.0)


if __name__ == "__main__":
    unittest.main()
