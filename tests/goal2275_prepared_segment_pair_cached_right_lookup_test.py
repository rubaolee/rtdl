from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2275_prepared_segment_pair_cached_right_lookup_2026-05-17.md"


class Goal2275PreparedSegmentPairCachedRightLookupTest(unittest.TestCase):
    def test_prepared_build_caches_right_lookup(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("struct PreparedSegmentPairIntersectionBuild")
        end = text.index("static void ensure_segment_pair_intersection_pipeline", start)
        struct_body = text[start:end]

        self.assertIn("std::unordered_map<uint32_t, const RtdlSegment*> right_by_id", struct_body)
        self.assertIn("right_by_id.reserve(count)", struct_body)
        self.assertIn("right_by_id.emplace(host_right_segments[i].id, &host_right_segments[i])", struct_body)

    def test_prepared_paths_reuse_cached_lookup(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        run_start = text.index("static void run_prepared_segment_pair_intersection_optix")
        run_end = text.index("static void count_prepared_segment_pair_intersection_optix", run_start)
        run_body = text[run_start:run_end]
        count_start = run_end
        count_end = text.index("static void run_ray_segment_group_count_2d_optix", count_start)
        count_body = text[count_start:count_end]

        self.assertIn("&prepared->right_by_id", run_body)
        self.assertIn("&prepared->right_by_id", count_body)

    def test_unprepared_path_keeps_local_lookup_fallback(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("prepared_right_by_id = nullptr", text)
        self.assertIn("std::unordered_map<uint32_t, const RtdlSegment*> local_right_by_id", text)
        self.assertIn("right_lookup = &local_right_by_id", text)

    def test_report_keeps_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("app-agnostic prepared-scene optimization", text)
        self.assertIn("not an LSI-specific", text)
        self.assertIn("does not claim a speedup by itself", text)


if __name__ == "__main__":
    unittest.main()
