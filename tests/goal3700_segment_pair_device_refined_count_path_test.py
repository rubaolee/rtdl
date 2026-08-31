from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs/reports/goal3700_segment_pair_device_refined_count_path_2026-06-07.md"


class Goal3700SegmentPairDeviceRefinedCountPathTest(unittest.TestCase):
    def test_device_refined_count_kernel_is_generic_and_exact_count_only(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("SegmentPairDeviceRefinedCountFunction", source)
        self.assertIn("segment_pair_device_refined_count_kernel", source)
        self.assertIn("exact_segment_intersection_device", source)
        self.assertIn("atomicAdd(exact_count, 1ull)", source)
        self.assertNotIn("rayjoin", source.lower())
        self.assertNotIn("cdb", source.lower())

    def test_device_refine_helper_exists_as_intermediate_count_route(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        block = source.split("static size_t count_segment_pair_intersection_candidates_device_refined_optix", 1)[1].split(
            "static size_t count_segment_pair_intersection_exact_one_pass_optix",
            1,
        )[0]

        self.assertIn("launch_segment_pair_device_refined_count_kernel", block)
        self.assertIn("d_left_exact_ptr,\n            left_count,", block)
        self.assertIn("g_optix_last_segment_pair_candidate_write_s", block)
        self.assertNotIn("g_optix_last_segment_pair_candidate_download_s +=", block)

    def test_device_kernel_uses_full_left_array_for_absolute_candidate_indices(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        block = source.split("static size_t count_segment_pair_intersection_candidates_device_refined_optix", 1)[1].split(
            "static void run_prepared_segment_pair_candidate_device_columns_optix",
            1,
        )[0]
        kernel = source.split("static const char* kSegmentPairDeviceRefinedCountKernelSrc", 1)[1].split(
            "struct SegmentFirstHitLaunchParams",
            1,
        )[0]

        self.assertIn("lp.left_offset = static_cast<uint32_t>(left_offset);", block)
        self.assertIn("candidate.left_index", kernel)
        self.assertIn("d_left_exact_ptr,\n            left_count,", block)
        self.assertNotIn("chunk_left_exact_ptr", block)

    def test_report_keeps_pod_and_claim_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("OptiX candidate traversal -> device-side exact segment-pair count", report)
        self.assertIn("row/witness route is intentionally unchanged", report)
        self.assertIn("not an app-specific RayJoin hook", report)
        self.assertIn("candidate download near zero", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
