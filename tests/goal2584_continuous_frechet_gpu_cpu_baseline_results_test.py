from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2584_continuous_frechet_gpu_cpu_baselines.py"
PLAN = ROOT / "docs" / "reports" / "goal2584_continuous_frechet_gpu_cpu_baseline_plan_2026-05-24.md"
REPORT = ROOT / "docs" / "reports" / "goal2584_continuous_frechet_gpu_cpu_baseline_results_2026-05-24.md"
RESULTS = ROOT / "docs" / "reports" / "goal2584_continuous_frechet_pod_results_2026-05-24.json"
LARGE = ROOT / "docs" / "reports" / "goal2584_continuous_frechet_pod_large_probe_2026-05-24.json"


class Goal2584ContinuousFrechetGpuCpuBaselineResultsTest(unittest.TestCase):
    def test_script_records_same_contract_gpu_and_cpu_baselines(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("torch_cuda_wavefront_all_cells", text)
        self.assertIn("cpu_cpp_all_cells", text)
        self.assertIn("rtdl_optix_broadphase_cpp", text)
        self.assertIn("torch_cuda_matches_cpu_cpp", text)
        self.assertIn("rtdl_optix_matches_cpu_cpp", text)

    def test_pod_result_json_records_correctness_for_all_rows(self) -> None:
        rows = []
        for path in (RESULTS, LARGE):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["environment"]["gpu"], "NVIDIA RTX A5000")
            rows.extend(payload["rows"])
        self.assertEqual([row["point_count_per_curve"] for row in rows], [32, 64, 128, 256, 512, 1024])
        for row in rows:
            with self.subTest(points=row["point_count_per_curve"]):
                self.assertTrue(row["torch_cuda_matches_cpu_cpp"])
                self.assertTrue(row["rtdl_optix_matches_cpu_cpp"])
                self.assertLess(row["rtdl_optix_over_cpu_cpp_speed"], 1.0)
                self.assertGreater(row["rtdl_optix_over_torch_cuda_speed"], 1.0)

    def test_reports_keep_claim_boundary(self) -> None:
        for path in (PLAN, REPORT):
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("same-contract", text)
                self.assertIn("not", text.lower())
                self.assertIn("public", text.lower())
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not beat the optimized CPU C++ all-cells baseline", report)
        self.assertIn("Claim not allowed", report)


if __name__ == "__main__":
    unittest.main()
