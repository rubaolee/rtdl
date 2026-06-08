from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3848_aabb_count_atomic_optimization_negative_probe_2026-06-08.md"


class Goal3848AabbCountAtomicOptimizationNegativeProbeTest(unittest.TestCase):
    def test_aabb_count_path_is_restored_to_known_correct_global_counter(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("const unsigned long long row_index = atomicAdd(params.hit_count, 1ULL);", text)
        self.assertIn("optixReportIntersection(hit_t, 0u);", text)
        self.assertIn("nullptr, 1).release();", text)
        self.assertNotIn("query_hit_counts", text)
        self.assertNotIn("sum_device_u32_counts", text)

    def test_report_records_rejected_fast_but_wrong_counts(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        flattened = " ".join(text.split())

        for phrase in (
            "Goal3848",
            "negative probe preserved",
            "fast but wrong",
            "point_contains=107557",
            "range_contains=11870",
            "range_intersects=428116",
            "known-correct Goal3846 baseline counts",
            "not a LibRTS-specific native customization request",
        ):
            self.assertIn(phrase, flattened)


if __name__ == "__main__":
    unittest.main()
