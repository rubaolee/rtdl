from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3848_aabb_count_per_ray_device_accumulation_2026-06-08.md"
BASELINE = ROOT / "docs" / "reports" / "goal3846_stress_probe_candidates_a5000" / "librts_131k_repeat10.json"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3848_aabb_per_ray_device_a5000"
    / "librts_131k_repeat10_per_ray_device_defaults.json"
)
STDERR = ARTIFACT.with_suffix(".stderr.txt")


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
            "1.1456x",
            "not LibRTS-specific",
            "does not authorize release action",
        ):
            self.assertIn(phrase, flattened)

    def test_a5000_artifact_matches_baseline_counts_and_improves_hot_query(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["counts"], baseline["counts"])
        self.assertEqual(artifact["fixture"]["box_count"], 131_072)
        self.assertEqual(artifact["fixture"]["point_query_count"], 131_072)
        self.assertEqual(artifact["fixture"]["box_query_count"], 131_072)
        self.assertEqual(artifact["repeat_protocol"]["repeat"], 10)
        self.assertEqual(artifact["repeat_protocol"]["warmup"], 2)
        self.assertTrue(artifact["rt_core_accelerated"])
        self.assertFalse(artifact["native_engine_customization"])
        self.assertLess(
            artifact["repeat_protocol"]["query_sec_median"],
            baseline["repeat_protocol"]["query_sec_median"],
        )
        self.assertGreater(
            baseline["repeat_protocol"]["query_sec_median"]
            / artifact["repeat_protocol"]["query_sec_median"],
            1.1,
        )
        self.assertEqual(STDERR.read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
