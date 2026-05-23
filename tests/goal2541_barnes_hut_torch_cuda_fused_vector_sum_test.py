from pathlib import Path
import json
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2541_barnes_hut_torch_cuda_fused_vector_sum_2026-05-23.md"
)
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"
SCRIPT = REPO_ROOT / "scripts" / "goal2541_barnes_hut_torch_cuda_fused_vector_sum.py"
CUDA_2048 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2541_barnes_hut_torch_cuda_fused_vector_sum_pod_2048_2026-05-23.json"
)
CUDA_8192 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2541_barnes_hut_torch_cuda_fused_vector_sum_pod_8192_2026-05-23.json"
)
CUDA_32768 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2541_barnes_hut_torch_cuda_fused_vector_sum_pod_32768_2026-05-23.json"
)
CPP_32768 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2541_barnes_hut_same_contract_cpp_baseline_pod_32768_2026-05-23.json"
)


class Goal2541BarnesHutTorchCudaFusedVectorSumTest(unittest.TestCase):
    def test_script_declares_generic_contract_and_torch_extension(self) -> None:
        text = SCRIPT.read_text()
        for phrase in [
            "torch.utils.cpp_extension",
            "fused_frontier_vector_sum_cuda",
            "AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT",
            "native_engine_app_specific",
            "authors_code_comparison",
            "public_speedup_claim_authorized",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_cuda_artifacts_match_reference_counts(self) -> None:
        for path in (CUDA_2048, CUDA_8192, CUDA_32768):
            payload = json.loads(path.read_text())
            with self.subTest(path=path.name):
                self.assertEqual(payload["backend"], "torch_cuda_extension")
                self.assertEqual(payload["contract"], "generic_aggregate_frontier_weighted_vector_sum_2d_v1")
                self.assertFalse(payload["metadata"]["native_engine_app_specific"])
                self.assertFalse(payload["metadata"]["public_speedup_claim_authorized"])
                self.assertEqual(payload["deltas"]["visited_node_total"], 0)
                self.assertEqual(payload["deltas"]["contribution_row_count"], 0)
                self.assertLess(payload["deltas"]["checksum_force_x_abs"], 1.0e-7)
                self.assertLess(payload["deltas"]["checksum_force_y_abs"], 1.0e-7)

    def test_large_cuda_point_beats_same_contract_cpp_16_thread_diagnostic(self) -> None:
        cuda_payload = json.loads(CUDA_32768.read_text())
        cpp_payload = json.loads(CPP_32768.read_text())
        cuda_ms = cuda_payload["timing_ms"]["resident_kernel_min"]
        cpp_16_ms = {run["threads"]: run for run in cpp_payload["runs"]}[16]["force_ms"]
        self.assertLess(cuda_ms, cpp_16_ms)
        self.assertEqual(
            cuda_payload["result"]["contribution_row_count"],
            cpp_payload["runs"][0]["contribution_row_count"],
        )
        self.assertEqual(
            cuda_payload["result"]["visited_node_total"],
            cpp_payload["runs"][0]["visited_node_total"],
        )

    def test_report_and_readme_capture_boundaries(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        for phrase in [
            "Torch/CUDA partner prototype",
            "not public speedup evidence",
            "resident CUDA kernel time",
            "prepared-tree lifetime",
            "device-resident state reuse",
            "not OptiX",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal2541_barnes_hut_torch_cuda_fused_vector_sum.py", readme_text)


if __name__ == "__main__":
    unittest.main()
