from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3572GroupedI64SmallGroupFullReductionFastPathTest(unittest.TestCase):
    def test_selector_covers_all_generic_grouped_i64_reductions(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        selector_start = text.index("const bool use_small_group_sum_count_fast_path")
        selector = text[selector_start : selector_start + 1800]

        for operation in ("kDeviceColumnGroupedOpSum", "kDeviceColumnGroupedOpSumCount"):
            self.assertIn(operation, selector)
        for operation in ("kDeviceColumnGroupedOpCount", "kDeviceColumnGroupedOpMin", "kDeviceColumnGroupedOpMax", "kDeviceColumnGroupedOpStats"):
            self.assertIn(operation, selector)
        self.assertIn("shared_memory_word_arrays = 2u", selector)
        self.assertIn("shared_memory_word_arrays = operation == kDeviceColumnGroupedOpCount", selector)
        self.assertIn("operation == kDeviceColumnGroupedOpStats ? 4u : 2u", selector)
        self.assertIn("g_device_column_grouped_i64.small_group_fn", selector)
        self.assertIn("g_device_column_grouped_i64.small_group_reduction_fn", selector)
        self.assertNotIn("raydb", selector.lower())
        self.assertNotIn("database", selector.lower())

    def test_kernel_has_shared_min_max_and_generic_flush_paths(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        kernel_start = text.index("extern \"C\" __global__ void device_column_grouped_i64_small_group_reduction_kernel")
        kernel = text[kernel_start : text.index("extern \"C\" __global__ void device_column_grouped_i64_compact_count_kernel")]
        sum_kernel_start = text.index("extern \"C\" __global__ void device_column_grouped_i64_small_group_kernel")
        sum_kernel = text[sum_kernel_start:kernel_start]

        self.assertIn("const bool needs_sum = params.operation == RTDL_GROUPED_OP_SUM", kernel)
        self.assertIn("const bool needs_min = params.operation == RTDL_GROUPED_OP_MIN", kernel)
        self.assertIn("const bool needs_max = params.operation == RTDL_GROUPED_OP_MAX", kernel)
        self.assertIn("? shared_sums + params.group_capacity", kernel)
        self.assertIn("? shared_mins + params.group_capacity", kernel)
        self.assertIn("const long long i64_max_value = 9223372036854775807LL", kernel)
        self.assertIn("const long long i64_min_value = (-9223372036854775807LL - 1LL)", kernel)
        self.assertIn("params.operation == RTDL_GROUPED_OP_MIN", kernel)
        self.assertIn("params.operation == RTDL_GROUPED_OP_MAX", kernel)
        self.assertIn("params.operation == RTDL_GROUPED_OP_STATS", kernel)
        self.assertIn("device_atomic_min_i64(reinterpret_cast<long long*>(params.group_sums) + group", kernel)
        self.assertIn("device_atomic_max_i64(reinterpret_cast<long long*>(params.group_sums) + group", kernel)
        self.assertIn("device_atomic_min_i64(reinterpret_cast<long long*>(params.group_mins) + group", kernel)
        self.assertIn("device_atomic_max_i64(reinterpret_cast<long long*>(params.group_maxs) + group", kernel)
        self.assertIn("atomicAdd(shared_sums + group, static_cast<unsigned long long>(value))", sum_kernel)
        self.assertNotIn("device_atomic_min_i64", sum_kernel)
        self.assertNotIn("device_atomic_max_i64", sum_kernel)
        self.assertNotIn("raydb", kernel.lower())
        self.assertNotIn("database", kernel.lower())


if __name__ == "__main__":
    unittest.main()
