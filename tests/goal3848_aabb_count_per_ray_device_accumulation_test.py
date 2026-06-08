from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3848_aabb_count_per_ray_device_accumulation_2026-06-08.md"


class Goal3848AabbCountPerRayDeviceAccumulationTest(unittest.TestCase):
    def test_count_only_aabb_path_uses_intersection_program_per_ray_counters(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("uint32_t* query_hit_counts;", text)
        self.assertIn("atomicAdd(params.query_hit_counts + qidx, 1u)", text)
        self.assertIn("if (params.collect_rows == 0u)", text)
        self.assertIn("sum_device_u32_counts", text)
        self.assertIn("const unsigned long long row_index = atomicAdd(params.hit_count, 1ULL);", text)
        self.assertIn("nullptr, 1).release();", text)

    def test_report_records_command_mismatch_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        flattened = " ".join(text.split())

        for phrase in (
            "Goal3848",
            "AABB_INDEX_QUERY_2D",
            "single global count hot spot",
            "distributed per-ray device counters",
            "Validation Note",
            "README smoke widths",
            "same smaller counts",
            "not LibRTS-specific",
            "does not authorize release action",
        ):
            self.assertIn(phrase, flattened)


if __name__ == "__main__":
    unittest.main()
