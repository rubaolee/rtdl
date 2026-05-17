from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2269_prepared_segment_pair_intersection_count_mode_2026-05-17.md"


class Goal2269PreparedSegmentPairIntersectionCountModeTest(unittest.TestCase):
    def test_native_count_symbol_is_generic(self) -> None:
        symbol = "rtdl_optix_count_prepared_segment_pair_intersection"

        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, API.read_text(encoding="utf-8"))
        self.assertIn("count_prepared_segment_pair_intersection_optix", WORKLOADS.read_text(encoding="utf-8"))

    def test_count_path_avoids_final_row_allocation(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("static void count_prepared_segment_pair_intersection_optix")
        end = text.index("static void run_ray_segment_group_count_2d_optix", start)
        count_body = text[start:end]

        self.assertNotIn("run_prepared_segment_pair_intersection_optix(", count_body)
        self.assertNotIn("RtdlSegmentPairIntersectionRow* rows", count_body)
        self.assertIn("collect_segment_pair_intersection_candidates_optix", count_body)
        self.assertIn("count_segment_pair_intersection_rows", count_body)
        self.assertIn("*count_out = count_segment_pair_intersection_rows", count_body)

    def test_count_path_preserves_exact_refinement(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("static size_t count_segment_pair_intersection_rows")
        end = text.index("static std::vector<GpuSegmentPairIntersectionRecord>", start)
        count_body = text[start:end]

        self.assertIn("exact_segment_intersection", count_body)
        self.assertIn("seen_pairs", count_body)
        self.assertIn("++exact_count", count_body)

    def test_python_prepared_count_surface(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def count(self, left_segments) -> int:", runtime)
        self.assertIn("rtdl_optix_count_prepared_segment_pair_intersection", runtime)
        self.assertIn("ctypes.POINTER(ctypes.c_size_t)", runtime)

    def test_report_keeps_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("generic count-only surface", text)
        self.assertIn("not an LSI-specific primitive", text)
        self.assertIn("not a RayJoin-specific primitive", text)
        self.assertIn("pod timing must be recorded separately", text)


if __name__ == "__main__":
    unittest.main()
