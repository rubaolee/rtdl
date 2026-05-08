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
        core = CORE_CPP.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT", api)
        self.assertIn("RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL", api)
        self.assertIn("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT", api)
        self.assertIn("RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS", api)
        self.assertIn("RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS", api)
        self.assertIn("RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE", api)
        self.assertIn("collect_k_use_cub_tile_sort", api)
        self.assertIn("collect_k_use_device_prefix_compact", api)
        self.assertIn("collect_k_use_derived_level_descriptors", api)
        self.assertIn("collect_k_use_device_level_counts", api)
        self.assertIn("collect_k_reuse_workspace", api)
        self.assertIn("if (use_cub_tile_sort)", api)
        self.assertIn("launch_cub_sort_tiles", api)
        self.assertIn("CollectKRowWidth2Workspace", api)
        self.assertIn("g_collect_k_row_width2_workspace_mutex", api)
        self.assertIn("collect_k_bounded_i64_row_width2_final_prefix_offsets_level", core)
        self.assertIn("collect_k_bounded_i64_row_width2_final_materialize_level_derived", core)
        self.assertIn("collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived", core)
        self.assertIn("collect_k_bounded_i64_row_width2_final_mark_counts_level_counts", core)
        self.assertIn("collect_k_bounded_i64_row_width2_final_compact_level_derived", core)

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
        self.assertIn("collect_k_bounded_i64_row_width2_cub_sort_tiles", source)
        self.assertIn("return lhs.second < rhs.second", source)
        self.assertIn("INT64_MAX", source)
        self.assertNotIn("uint64_t packed", source)

    def test_cub_topology_uses_smaller_tiles(self) -> None:
        old_value = os.environ.get("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT")
        os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = "1"
        try:
            self.assertEqual(probe.expected_topology(4097, 2)["tile_count"], 3)
            self.assertEqual(probe.expected_topology(4097, 2)["sort_launches"], 1)
            self.assertEqual(probe.expected_topology(65537, 2)["tile_count"], 33)
            self.assertEqual(probe.expected_topology(65537, 2)["sort_launches"], 1)
            self.assertEqual(probe.expected_topology(131072, 2)["tile_count"], 64)
            self.assertEqual(probe.expected_topology(131072, 2)["sort_launches"], 1)
        finally:
            if old_value is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = old_value

    def test_parallel_compact_threshold_is_topology_visible(self) -> None:
        old_compact = os.environ.get("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT")
        old_threshold = os.environ.get("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY")
        os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY"] = "16384"
        try:
            topology = probe.expected_topology(131072, 2)
        finally:
            if old_compact is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = old_compact
            if old_threshold is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY"] = old_threshold

        self.assertEqual(topology["merge_launches"], 46)
        self.assertEqual(topology["final_copies"], 0)

    def test_cub_tile_sort_defaults_to_early_parallel_compact(self) -> None:
        old_cub = os.environ.get("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT")
        old_compact = os.environ.get("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT")
        old_threshold = os.environ.get("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY")
        os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = "1"
        os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY", None)
        try:
            topology = probe.expected_topology(131072, 2)
        finally:
            if old_cub is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = old_cub
            if old_compact is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = old_compact
            if old_threshold is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY"] = old_threshold

        self.assertEqual(topology["tile_count"], 64)
        self.assertEqual(topology["merge_launches"], 189)
        self.assertEqual(topology["metadata_fields_downloaded"], 191)

    def test_batched_compact_level_topology_reduces_merge_launches(self) -> None:
        saved = {
            name: os.environ.get(name)
            for name in (
                "RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT",
                "RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT",
                "RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL",
                "RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY",
            )
        }
        os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL"] = "1"
        os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY", None)
        try:
            topology = probe.expected_topology(131072, 2)
        finally:
            for name, value in saved.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        self.assertEqual(topology["tile_count"], 64)
        self.assertEqual(topology["sort_launches"], 1)
        self.assertEqual(topology["merge_launches"], 18)

    def test_device_prefix_compact_topology_is_env_gated(self) -> None:
        saved = {
            name: os.environ.get(name)
            for name in (
                "RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT",
                "RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT",
                "RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL",
                "RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT",
                "RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY",
            )
        }
        os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT"] = "1"
        os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY", None)
        try:
            topology = probe.expected_topology(131072, 2)
        finally:
            for name, value in saved.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        self.assertEqual(topology["tile_count"], 64)
        self.assertEqual(topology["sort_launches"], 1)
        self.assertEqual(topology["merge_launches"], 23)

    def test_device_level_counts_topology_reduces_metadata_downloads(self) -> None:
        saved = {
            name: os.environ.get(name)
            for name in (
                "RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT",
                "RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT",
                "RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL",
                "RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT",
                "RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS",
                "RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS",
                "RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY",
            )
        }
        os.environ["RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS"] = "1"
        os.environ["RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS"] = "1"
        os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY", None)
        try:
            topology = probe.expected_topology(131072, 2)
        finally:
            for name, value in saved.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        self.assertEqual(topology["tile_count"], 64)
        self.assertEqual(topology["merge_launches"], 23)
        self.assertEqual(topology["metadata_fields_downloaded"], 131)


if __name__ == "__main__":
    unittest.main()
