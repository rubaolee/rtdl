import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DRIVER_LOADED_PTX_KERNELS: tuple[str, ...] = ()


def _driver_loaded_ptx_kernel_names() -> tuple[str, ...]:
    names: list[str] = []
    for path in (
        ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp",
        ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp",
    ):
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for index, line in enumerate(lines):
            if "cuModuleLoadData" not in line or "ptx.c_str()" not in line:
                continue
            block = "\n".join(lines[max(0, index - 8) : index + 2])
            matches = re.findall(r'"([^"]+\.cu)"', block)
            if matches:
                names.append(matches[-1])
    return tuple(names)


class Goal3951DirectCudaPtxLoaderDebtInventoryTest(unittest.TestCase):
    def test_remaining_driver_loaded_ptx_sites_match_inventory(self) -> None:
        self.assertEqual(
            EXPECTED_DRIVER_LOADED_PTX_KERNELS,
            _driver_loaded_ptx_kernel_names(),
        )

    def test_recently_hardened_neighbor_kernels_are_not_in_ptx_debt(self) -> None:
        remaining = set(_driver_loaded_ptx_kernel_names())
        for kernel in (
            "frn3d_kernel.cu",
            "frn3d_grid_kernel.cu",
            "pns_kernel.cu",
            "frn_kernel.cu",
            "partner_point2d_fixed_radius_aabb_pack_kernel.cu",
            "k_closest_hits_kernel.cu",
            "knn3d_kernel.cu",
            "device_column_grouped_i64_kernel.cu",
            "segment_pair_ambiguity_count_kernel.cu",
            "segment_pair_device_refined_count_kernel.cu",
            "partner_triangle3d_device_columns_pack_kernel.cu",
            "partner_ray3d_device_columns_pack_kernel.cu",
            "partner_triangle2d_device_columns_pack_kernel.cu",
            "partner_ray2d_device_columns_pack_kernel.cu",
            "point_group_nearest_split_columns_kernel.cu",
            "point_group_nearest_max_reduce_kernel.cu",
            "collect_k_cooperative_launch_smoke_kernel.cu",
            "collect_k_bounded_i64_row_width2_sort_kernel.cu",
            "collect_k_bounded_i64_row_width2_cub_sort_kernel.cu",
            "collect_k_bounded_i64_row_width2_merge_two_kernel.cu",
            "collect_k_bounded_i64_row_width2_merge_level_kernel.cu",
            "collect_k_bounded_i64_row_width2_final_compact_kernel.cu",
            "collect_k_bounded_i64_kernel.cu",
        ):
            self.assertNotIn(kernel, remaining)


if __name__ == "__main__":
    unittest.main()
