from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2207_optix_segment_pair_chunked_capacity_2026-05-17.md"


class Goal2207OptixSegmentPairChunkedCapacityTest(unittest.TestCase):
    def test_optix_segment_pair_intersection_chunks_large_cartesian_spaces(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertNotIn("segment-pair intersection output capacity exceeds uint32_t", text)
        self.assertIn("max_left_per_launch64", text)
        self.assertIn("left_offset < left_count; left_offset += max_left_per_launch", text)
        self.assertIn("chunk_left_ptr", text)
        self.assertIn("static_cast<unsigned>(chunk_left_count)", text)
        self.assertIn("gpu_rows.resize(old_size + gpu_count)", text)

    def test_report_records_the_rayjoin_same_query_failure_and_fix_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2207", text)
        self.assertIn("Goal2198 r4", text)
        self.assertIn("segment-pair intersection output capacity exceeds uint32_t", text)
        self.assertIn("chunked OptiX segment-pair launches", text)
        self.assertIn("app-agnostic", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
