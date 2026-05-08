from pathlib import Path
import os
import unittest

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal1539V154OptixCollectKCubTileSortRuntimeTest(unittest.TestCase):
    def test_cub_tile_sort_is_env_gated(self) -> None:
        api = API_CPP.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT", api)
        self.assertIn("collect_k_use_cub_tile_sort", api)
        self.assertIn("if (use_cub_tile_sort)", api)

    def test_default_bitonic_sort_kernel_remains_available(self) -> None:
        source = CORE_CPP.read_text(encoding="utf-8")
        api = API_CPP.read_text(encoding="utf-8")

        self.assertIn("collect_k_bounded_i64_row_width2_sort", source)
        self.assertIn("kCollectKBoundedI64RowWidth2SortKernelSrc", api)
        self.assertIn("g_collect_k_i64_row_width2_sort.fn", api)

    def test_cub_kernel_uses_full_row_comparator_without_key_packing(self) -> None:
        source = CORE_CPP.read_text(encoding="utf-8")

        self.assertIn("#include <cub/block/block_merge_sort.cuh>", source)
        self.assertIn("constexpr int items_per_thread = 8", source)
        self.assertIn("cub::BlockMergeSort<CollectKRow2, block_threads, items_per_thread>", source)
        self.assertIn("return lhs.second < rhs.second", source)
        self.assertIn("INT64_MAX", source)
        self.assertNotIn("uint64_t packed", source)

    def test_cub_topology_uses_smaller_tiles(self) -> None:
        old_value = os.environ.get("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT")
        os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = "1"
        try:
            self.assertEqual(probe.expected_topology(4097, 2)["tile_count"], 3)
            self.assertEqual(probe.expected_topology(65537, 2)["tile_count"], 33)
            self.assertEqual(probe.expected_topology(131072, 2)["tile_count"], 64)
        finally:
            if old_value is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = old_value


if __name__ == "__main__":
    unittest.main()
