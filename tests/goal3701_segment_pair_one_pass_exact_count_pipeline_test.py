from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
COMPOSITE = ROOT / "scripts/goal3612_rayjoin_safe_mixed_route_composite.py"
REPORT = ROOT / "docs/reports/goal3701_segment_pair_one_pass_exact_count_pipeline_2026-06-07.md"


class Goal3701SegmentPairOnePassExactCountPipelineTest(unittest.TestCase):
    def test_exact_count_pipeline_is_generic_and_one_pass(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("SegmentPairExactCountLaunchParams", source)
        self.assertIn("g_segment_pair_exact_count", source)
        self.assertIn("ensure_segment_pair_exact_count_pipeline", source)
        self.assertIn("segment_pair_exact_count_kernel.cu", source)
        self.assertIn("exact_segment_intersection_device", source)
        self.assertIn("atomicAdd(params.exact_count, 1ull)", source)
        self.assertNotIn("rayjoin", source.lower())
        self.assertNotIn("cdb", source.lower())

    def test_prepared_scalar_count_route_uses_one_pass_exact_count(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        block = source.split("static void count_prepared_segment_pair_intersection_optix", 1)[1].split(
            "static void run_prepared_segment_first_hit_optix",
            1,
        )[0]

        self.assertIn("DevPtr d_left_exact(sizeof(RtdlSegment) * left_count);", block)
        self.assertIn("count_segment_pair_intersection_exact_one_pass_optix", block)
        self.assertNotIn("count_segment_pair_intersection_candidates_device_refined_optix(", block)
        self.assertNotIn("collect_segment_pair_intersection_candidates_optix", block)
        self.assertNotIn("count_segment_pair_intersection_rows", block)

    def test_one_pass_route_avoids_candidate_write_and_download_counters(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        block = source.split("static size_t count_segment_pair_intersection_exact_one_pass_optix", 1)[1].split(
            "static void run_prepared_segment_pair_candidate_device_columns_optix",
            1,
        )[0]

        self.assertIn("candidate_event_count", block)
        self.assertIn("g_optix_last_segment_pair_candidate_count_s +=", block)
        self.assertNotIn("g_optix_last_segment_pair_candidate_write_s +=", block)
        self.assertNotIn("g_optix_last_segment_pair_candidate_download_s +=", block)

    def test_rayjoin_helper_metadata_no_longer_says_host_refine(self) -> None:
        text = COMPOSITE.read_text(encoding="utf-8")

        self.assertIn("device_double_exact_count_during_optix_anyhit", text)
        self.assertNotIn("host_double_exact_refine_after_optix_candidates", text)

    def test_report_keeps_pod_and_claim_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("one OptiX traversal pass -> exact double predicate in any-hit", report)
        self.assertIn("row/witness mode remains unchanged", report)
        self.assertIn("not a RayJoin-specific engine path", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
