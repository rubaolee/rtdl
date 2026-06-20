from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "v2_v3_v4_large_scale_performance_comparison_2026-06-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "v2_v3_v4_large_scale_performance_2026-06-19"
CURRENT_SCALE = ARTIFACT_DIR / "lx1_current_benchmark_scale_profile_2026-06-19.json"
V4_PROBE = ARTIFACT_DIR / "lx1_v4_m1_fixed_radius_cupy_262k_probe_2026-06-19.json"
HAUSDORFF_SUPPLEMENT = ARTIFACT_DIR / "large_supplements" / "hausdorff_xhd_1m_threshold.stdout.json"
TRIANGLE_SUPPLEMENT = (
    ARTIFACT_DIR / "large_supplements" / "triangle_counting_rt_graph_2a1_65536.stdout.json"
)


EXPECTED_APPS = {
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rt_dbscan",
    "robot_collision",
    "contact_manifold",
    "raydb_style",
    "barnes_hut",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
}


class V2V3V4LargeScalePerformanceReportTest(unittest.TestCase):
    def test_report_keeps_generation_boundaries_explicit(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for token in (
            "RTDL V2.x / V3 / V4 Large-Scale Performance Comparison",
            "not release authorization",
            "V2.14 is the strongest public performance baseline",
            "V3.0.2 is not a new broad speedup release",
            "V4.0 is not an all benchmark-app performance suite",
            "10/10 rows passed",
            "Connection refused",
            "Pod-ready rerun command",
            "v4_0_m1_linux_gpu_release_gate.py",
            "benchmark-count 262144",
            "This packet does not claim",
            "V4.0 is faster than V3.0.2",
            "GTX 1070 timing proves RTX/RT-core speedup",
        ):
            self.assertIn(token, text)

    def test_current_scale_profile_covers_all_apps_with_claim_flags_blocked(self) -> None:
        payload = json.loads(CURRENT_SCALE.read_text(encoding="utf-8"))

        self.assertTrue(payload["all_pass"])
        self.assertEqual(10, len(payload["rows"]))
        self.assertEqual(EXPECTED_APPS, {row["app"] for row in payload["rows"]})
        self.assertEqual(10, payload["json_pass_count"])
        self.assertEqual("6d2193af16f8269f3e901124593dacc43335255b", payload["runtime_environment"]["source_commit"])
        self.assertIn("NVIDIA GeForce GTX 1070", payload["runtime_environment"]["nvidia_smi"])

        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertFalse(payload[key], key)

        for row in payload["rows"]:
            self.assertEqual("pass", row["status"], row["row_id"])
            self.assertTrue(row["semantic_stdout_check"]["stdout_json_parseable"], row["row_id"])
            self.assertFalse(row["semantic_stdout_check"]["claim_flag_violations"], row["row_id"])

    def test_large_supplements_are_serious_scale_and_parseable(self) -> None:
        hausdorff = json.loads(HAUSDORFF_SUPPLEMENT.read_text(encoding="utf-8"))
        triangle = json.loads(TRIANGLE_SUPPLEMENT.read_text(encoding="utf-8"))

        self.assertEqual(1_048_576, hausdorff["point_count_a"])
        self.assertEqual(1_048_576, hausdorff["point_count_b"])
        self.assertTrue(hausdorff["matches_oracle"])
        self.assertTrue(hausdorff["oracle_decision_matches"])
        self.assertGreater(hausdorff["run_phases"]["query_fixed_radius_threshold_reached_count_sec"], 1.0)

        self.assertEqual(131_072, triangle["ray_count"])
        self.assertEqual(327_680, triangle["primitive_count"])
        self.assertTrue(triangle["triangle_count_matches_oracle"])
        self.assertGreater(triangle["timing_ms"]["query_median_ms"], 1.0)

    def test_v4_large_probe_remains_route_scoped_non_authorizing(self) -> None:
        payload = json.loads(V4_PROBE.read_text(encoding="utf-8"))

        self.assertEqual("pass-with-boundary", payload["status"])
        self.assertEqual(262_144, payload["parameters"]["count"])
        self.assertEqual("fixed_radius_count_threshold_2d", payload["route_id"])
        self.assertTrue(payload["validation"]["output_match"])
        self.assertGreater(payload["median_seconds"]["cupy_bruteforce_cuda_core_baseline"], 30.0)
        self.assertLess(payload["median_seconds"]["v4_prepared_query_only"], 0.01)

        boundaries = payload["claim_boundaries"]
        for key in (
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "v4_true_zero_copy_claim_authorized",
            "async_claim_authorized",
        ):
            self.assertFalse(boundaries[key], key)


if __name__ == "__main__":
    unittest.main()
