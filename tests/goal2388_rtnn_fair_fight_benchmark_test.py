import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
POD_RUNNER = ROOT / "scripts" / "goal2388_rtnn_fair_fight_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2388_rtnn_fair_fight_benchmark_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2388_rtnn_fair_fight_pod"


def _load(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal2388RtnnFairFightBenchmarkTest(unittest.TestCase):
    def test_runner_exposes_batched_rtdl_and_cupy_fair_baseline(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        pod_runner = POD_RUNNER.read_text(encoding="utf-8")

        self.assertIn("run-rtdl-batched-3d-neighbors", runner)
        self.assertIn("run-cupy-3d-ranked-summary", runner)
        self.assertIn("distribution", runner)
        self.assertIn("partitioned_or_batched_like_rtnn", runner)
        self.assertIn("cuda_core_baseline", runner)
        self.assertIn("paper_equivalent_rtnn_row", runner)

        self.assertIn("DISTRIBUTIONS", pod_runner)
        self.assertIn("RTDL_COUNTS", pod_runner)
        self.assertIn("CUPY_COUNTS", pod_runner)
        self.assertIn("RTNN_BINARY=\"$(realpath \"$RTNN_BINARY\")\"", pod_runner)
        self.assertIn("--result-mode ranked-summary-raw", pod_runner)

    def test_report_preserves_claim_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("This is not a full RTNN paper reproduction", report)
        self.assertIn("No RTNN-specific native symbol", report)
        self.assertIn("not an optimized grid/BVH CUDA implementation", report)
        self.assertIn("not a same-algorithm comparison", report)
        self.assertIn("does not prove a broad nearest-neighbor speedup", report)
        self.assertIn("Not authorized", report)
        self.assertIn("density-aware/adaptive prepared partitioning", report)

    def test_pod_artifacts_show_rtdl_vs_cupy_gain_and_rtnn_boundary(self) -> None:
        expected_min_ratio = {
            "uniform": 1000.0,
            "clustered": 50.0,
            "shell": 1000.0,
        }
        for distribution, min_ratio in expected_min_ratio.items():
            rtdl = _load(f"rtdl_batched_ranked_summary_{distribution}_65536_r002_k50.json")
            cupy = _load(f"cupy_exact_ranked_summary_{distribution}_65536_r002_k50.json")
            self.assertTrue(rtdl["ok"])
            self.assertTrue(cupy["ok"])
            self.assertEqual(rtdl["contract"]["family"], "fixed_radius_neighbors_3d")
            self.assertTrue(rtdl["contract"]["exact"])
            self.assertFalse(rtdl["contract"]["approximate"])
            self.assertTrue(rtdl["claim_boundary"]["partitioned_or_batched_like_rtnn"])
            self.assertFalse(rtdl["claim_boundary"]["paper_equivalent_rtnn_row"])
            self.assertTrue(cupy["claim_boundary"]["cuda_core_baseline"])
            self.assertFalse(cupy["claim_boundary"]["uses_rt_cores"])
            self.assertGreater(cupy["elapsed_sec"] / rtdl["elapsed_sec"], min_ratio)

        for distribution in ("uniform", "clustered", "shell"):
            large = _load(f"rtdl_batched_ranked_summary_{distribution}_262144_r002_k50.json")
            self.assertTrue(large["ok"])
            self.assertEqual(large["row_count"], 262144)
            self.assertEqual(large["result_mode"], "ranked-summary-raw")

        status = _load("rtnn_status.json")
        self.assertTrue(status["available"])
        official = _load("rtnn_official_radius_uniform_65536_r002_k50.json")
        self.assertEqual(official["returncode"], 0)
        self.assertFalse(official["claim_boundary"]["full_rtnn_reproduction"])
        clustered_large = _load("rtnn_official_radius_clustered_262144_r002_k50.json")
        self.assertNotEqual(clustered_large["returncode"], 0)
        self.assertIn("out of memory", "\n".join(clustered_large["stderr_tail"]).lower())


if __name__ == "__main__":
    unittest.main()
