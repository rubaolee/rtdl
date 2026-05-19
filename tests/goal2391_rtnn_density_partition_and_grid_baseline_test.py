import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
POD_RUNNER = ROOT / "scripts" / "goal2391_rtnn_density_partition_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2391_rtnn_density_partition_and_grid_baseline_2026-05-19.md"
FUTURE = ROOT / "docs" / "research" / "future_version_to_do_list.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2391_rtnn_density_partition_pod"
GOAL2388_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2388_rtnn_fair_fight_pod"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2391RtnnDensityPartitionAndGridBaselineTest(unittest.TestCase):
    def test_runner_exposes_adaptive_rtdl_and_grid_cupy_modes(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        pod_runner = POD_RUNNER.read_text(encoding="utf-8")

        self.assertIn("run-rtdl-adaptive-3d-neighbors", runner)
        self.assertIn("density_aware_spatial_partitioning", runner)
        self.assertIn("run-cupy-grid-3d-ranked-summary", runner)
        self.assertIn("cupy_cuda_core_grid_exact_ranked_summary_3d", runner)
        self.assertIn("stronger_than_all_pairs_baseline", runner)
        self.assertIn("native_abi_changed_for_rtnn", runner)

        self.assertIn("ADAPTIVE_DIVISIONS", pod_runner)
        self.assertIn("run-rtdl-adaptive-3d-neighbors", pod_runner)
        self.assertIn("run-cupy-grid-3d-ranked-summary", pod_runner)

    def test_report_and_future_todo_preserve_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        future = FUTURE.read_text(encoding="utf-8")

        self.assertIn("measured and rejected", report)
        self.assertIn("not an optimization", report)
        self.assertIn("stronger exact CUDA-core grid baseline", report)
        self.assertIn("No RTNN-specific native ABI", report)
        self.assertIn("not a full RTNN paper reproduction", report)
        self.assertIn("Goal2391 showed that Python-level density-aware partitioning", future)
        self.assertIn("generic CUDA-grid partner backend", future)

    def test_pod_artifacts_show_grid_baseline_and_adaptive_negative_result(self) -> None:
        rtdl = _load(ARTIFACT_DIR / "rtdl_batched_clustered_262144_r002_k50.json")
        adaptive = _load(ARTIFACT_DIR / "rtdl_adaptive_clustered_262144_div8_r002_k50.json")
        grid_large = _load(ARTIFACT_DIR / "cupy_grid_clustered_262144_r002_k50.json")

        self.assertTrue(rtdl["ok"])
        self.assertTrue(adaptive["ok"])
        self.assertTrue(grid_large["ok"])
        self.assertFalse(adaptive["claim_boundary"]["native_abi_changed_for_rtnn"])
        self.assertTrue(adaptive["claim_boundary"]["density_aware_partition_policy"])
        self.assertGreater(adaptive["elapsed_sec"] / rtdl["elapsed_sec"], 2.0)
        self.assertGreater(rtdl["elapsed_sec"] / grid_large["elapsed_sec"], 2.0)
        self.assertTrue(grid_large["claim_boundary"]["stronger_than_all_pairs_baseline"])
        self.assertFalse(grid_large["claim_boundary"]["uses_rt_cores"])

        for distribution in ("uniform", "clustered", "shell"):
            grid = _load(ARTIFACT_DIR / f"cupy_grid_{distribution}_65536_r002_k50.json")
            all_pairs = _load(GOAL2388_ARTIFACT_DIR / f"cupy_exact_ranked_summary_{distribution}_65536_r002_k50.json")
            self.assertTrue(grid["ok"])
            self.assertEqual(
                grid["summary"]["bounded_neighbor_count"],
                all_pairs["summary"]["bounded_neighbor_count"],
            )
            self.assertGreater(all_pairs["elapsed_sec"] / grid["elapsed_sec"], 100.0)


if __name__ == "__main__":
    unittest.main()
