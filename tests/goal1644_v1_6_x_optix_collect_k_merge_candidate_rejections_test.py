import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1644_v1_6_x_optix_collect_k_merge_chain_candidate_rejections_2026-05-09.md"


class Goal1644OptixCollectKMergeCandidateRejectionsTest(unittest.TestCase):
    def test_rejected_large_cub_tile_flags_are_not_retained(self) -> None:
        api = API.read_text(encoding="utf-8")
        core = CORE.read_text(encoding="utf-8")

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT_4096_DIAGNOSTIC", api)
        self.assertNotIn("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT_3072_DIAGNOSTIC", api)
        self.assertNotIn("collect_k_bounded_i64_row_width2_cub_sort_tiles_4096", core)
        self.assertNotIn("collect_k_bounded_i64_row_width2_cub_sort_tiles_3072", core)

    def test_fallback_merge_preserves_device_counts_contract_for_opt_in_sweeps(self) -> None:
        api = API.read_text(encoding="utf-8")
        start = api.rindex("std::vector<uint64_t> merge_first_rows(max_tile_segments);")
        fallback = api[start:api.index("upload(merge_first_rows_device.ptr, merge_first_rows.data(), pair_count);", start)]

        self.assertIn("if (use_device_level_counts)", fallback)
        self.assertIn("download(current_counts.data(), current_counts_level_device, current_rows.size())", fallback)
        self.assertIn("upload(next_counts_level_device, next_counts.data(), next_counts.size())", api)
        self.assertIn("std::swap(current_counts_level_device, next_counts_level_device)", api)

    def test_report_records_rejections_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`no_good_candidate_yet`", text)
        self.assertIn("CUDA driver error: invalid argument", text)
        self.assertIn("1.08 ms", text)
        self.assertIn("No larger CUB tile diagnostic flag is retained", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
