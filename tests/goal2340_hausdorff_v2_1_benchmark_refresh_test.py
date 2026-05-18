from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2340_hausdorff_v2_1_benchmark_refresh_2026-05-18.md"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_function.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "README.md"
HARNESS = ROOT / "scripts" / "goal2126_public_hausdorff_dataset_perf.py"
RUNNER = ROOT / "scripts" / "goal2340_hausdorff_v2_1_pod_runner.sh"


class Goal2340HausdorffV21BenchmarkRefreshTest(unittest.TestCase):
    def test_scale_aware_group_default_is_available_and_bounded(self) -> None:
        from examples import rtdl_hausdorff_v2_function as hd

        self.assertEqual(hd.default_target_points_per_group(1024), 64)
        self.assertEqual(hd.default_target_points_per_group(8192), 64)
        self.assertEqual(hd.default_target_points_per_group(131072), 1024)
        self.assertEqual(hd.default_target_points_per_group(262144), 2048)
        self.assertEqual(hd.default_target_points_per_group(524288), 4096)
        self.assertEqual(hd.default_target_points_per_group(1048576), 8192)
        self.assertEqual(hd.default_target_points_per_group(2097152), 8192)

    def test_cli_and_public_harness_expose_reproducible_knobs(self) -> None:
        app = APP.read_text(encoding="utf-8")
        harness = HARNESS.read_text(encoding="utf-8")
        self.assertIn("--target-points-per-group", app)
        self.assertIn("--seed-sample-count", app)
        self.assertIn("default_target_points_per_group(points_b.shape[0])", harness)
        self.assertIn("target_points_per_group=args.target_points_per_group", app)
        self.assertIn("seed_sample_count=args.seed_sample_count", app)

    def test_docs_and_report_keep_claim_boundary(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("v2.1-compatible RTDL/OptiX path", readme)
        self.assertIn("scale-aware target group size", readme)
        self.assertIn("Do not use this directory to claim that RTDL universally beats X-HD", readme)
        self.assertIn("scripts/goal2340_hausdorff_v2_1_pod_runner.sh", report)
        self.assertIn("Fresh current-main pod performance claim: `needs-pod-evidence`", report)
        self.assertIn("universal CUDA-vs-RT speedup", report)
        self.assertIn("Full X-HD reproduction", report)

    def test_pod_runner_records_progress_and_outputs_expected_artifacts(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn("[goal2340] run xhd-graphics 262144 auto-group", runner)
        self.assertIn("[goal2340] run xhd-graphics 1048576 auto-group", runner)
        self.assertIn("goal2340_hausdorff_v2_1_pod", runner)
        self.assertIn("cupy-cuda12x", runner)
        self.assertIn("make build-optix", runner)

    def test_report_is_ascii_for_review_portability(self) -> None:
        REPORT.read_text(encoding="utf-8").encode("ascii")


if __name__ == "__main__":
    unittest.main()
