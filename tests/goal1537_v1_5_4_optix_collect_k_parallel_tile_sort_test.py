from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1537_v1_5_4_optix_collect_k_parallel_tile_sort_negative_result_2026-05-08.md"
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
PROBE = ROOT / "scripts" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py"


class Goal1537V154OptixCollectKParallelTileSortNegativeResultTest(unittest.TestCase):
    def test_report_records_rejected_tile_sort_path(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Rejected as an implementation path", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_PARALLEL_TILE_SORT", text)
        self.assertIn("CUDA driver error: invalid resource handle", text)
        self.assertIn("65537", text)

    def test_failed_prototype_is_not_left_in_source_or_probe(self) -> None:
        source = (
            API_CPP.read_text(encoding="utf-8")
            + CORE_CPP.read_text(encoding="utf-8")
            + PROBE.read_text(encoding="utf-8")
        )

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_PARALLEL_TILE_SORT", source)
        self.assertNotIn("collect_k_bounded_i64_row_width2_sort_tiles", source)
        self.assertNotIn("collect_k_use_parallel_tile_sort", source)

    def test_report_preserves_next_direction(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("sort remains the dominant remaining stage", text)
        self.assertIn("Do not commit the unstable runtime path", text)
        self.assertIn("No source changes from this failed prototype were committed", text)


if __name__ == "__main__":
    unittest.main()
