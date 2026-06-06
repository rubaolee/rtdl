from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3564GroupedI64SmallGroupSumFastPathTest(unittest.TestCase):
    def test_native_fast_path_is_generic_and_sum_scoped(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        self.assertIn("device_column_grouped_i64_small_group_kernel", text)
        self.assertIn("kDeviceColumnGroupedSmallCapacityFastPathMaxGroups = 1024u", text)
        self.assertIn("extern __shared__ unsigned long long shared[]", text)

        selector_start = text.index("const bool use_small_group_sum_fast_path")
        selector = text[selector_start : selector_start + 500]
        self.assertIn("operation == kDeviceColumnGroupedOpSum", selector)
        self.assertIn("operation == kDeviceColumnGroupedOpSumCount", selector)
        self.assertIn("group_capacity <= kDeviceColumnGroupedSmallCapacityFastPathMaxGroups", selector)
        self.assertNotIn("RayDB", selector)

    def test_fast_path_reduces_global_atomic_pressure_before_compaction(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        kernel_start = text.index("extern \"C\" __global__ void device_column_grouped_i64_small_group_kernel")
        kernel = text[kernel_start : text.index("extern \"C\" __global__ void device_column_grouped_i64_compact_count_kernel")]
        self.assertIn("shared_counts[group] = 0ull", kernel)
        self.assertIn("shared_sums[group] = 0ull", kernel)
        self.assertIn("atomicAdd(shared_counts + group, 1ull)", kernel)
        self.assertIn("atomicAdd(shared_sums + group", kernel)
        self.assertIn("atomicAdd(params.group_counts + group, count)", kernel)
        self.assertIn("atomicAdd(params.group_sums + group, shared_sums[group])", kernel)
        self.assertNotIn("raydb", kernel.lower())
        self.assertNotIn("database", kernel.lower())


if __name__ == "__main__":
    unittest.main()
