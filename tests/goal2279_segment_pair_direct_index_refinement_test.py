from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2279_segment_pair_direct_index_refinement_2026-05-17.md"


class Goal2279SegmentPairDirectIndexRefinementTest(unittest.TestCase):
    def test_device_candidate_record_carries_direct_indices(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index("struct SegmentPairIntersectionRecord")
        end = text.index("struct SegmentPairIntersectionParams", start)
        record_body = text[start:end]

        self.assertIn("unsigned int left_id, right_id", record_body)
        self.assertIn("unsigned int left_index, right_index", record_body)

    def test_anyhit_writes_left_offset_and_hit_index(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index("__anyhit__segment_pair_intersection_anyhit")
        end = text.index("extern \"C\" __global__ void __miss__pip_miss()", start)
        anyhit_body = text[start:end]

        self.assertIn("unsigned int  left_offset", text)
        self.assertIn("r.left_index = params.left_offset + pidx", anyhit_body)
        self.assertIn("r.right_index = bidx", anyhit_body)

    def test_host_candidate_record_and_launch_params_match_device(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("uint32_t left_id, right_id, left_index, right_index", core)
        self.assertIn("uint32_t          left_offset", workloads)
        self.assertIn("lp.left_offset = static_cast<uint32_t>(left_offset)", workloads)
        self.assertIn("segment-pair intersection direct candidate index exceeds uint32_t", workloads)

    def test_refinement_uses_direct_indices_before_fallback_maps(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        finalize_start = text.index("static void finalize_segment_pair_intersection_rows")
        finalize_end = text.index("static size_t count_segment_pair_intersection_rows", finalize_start)
        finalize_body = text[finalize_start:finalize_end]
        count_start = finalize_end
        count_end = text.index("static std::vector<GpuSegmentPairIntersectionRecord>", count_start)
        count_body = text[count_start:count_end]

        for body in (finalize_body, count_body):
            self.assertIn("if (gpu_row.left_index < left_count && gpu_row.right_index < right_count)", body)
            self.assertIn("left_seg = &left[gpu_row.left_index]", body)
            self.assertIn("right_seg = &right[gpu_row.right_index]", body)
            self.assertIn("left_by_id", body)
            self.assertIn("local_right_by_id", body)
            self.assertIn("prepared_right_by_id", body)
            self.assertIn("exact_segment_intersection(*left_seg, *right_seg", body)

    def test_report_keeps_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("app-agnostic internal optimization", text)
        self.assertIn("not an LSI-specific primitive", text)
        self.assertIn("not a RayJoin-specific primitive", text)
        self.assertIn("does not claim a speedup by itself", text)
        self.assertIn("Pod timing should compare", text)


if __name__ == "__main__":
    unittest.main()
