from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2540_barnes_hut_benchmark_app_closeout_2026-05-23.md"
)
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"
SCRIPT = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "barnes_hut"
    / "rtdl_barnes_hut_benchmark_app.py"
)


class Goal2540BarnesHutBenchmarkAppCloseoutTest(unittest.TestCase):
    def test_closeout_records_contracts_and_runtime_lessons(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "generic_aggregate_opening_rows_2d_v1",
            "generic_bucketized_aggregate_tree_2d_v1",
            "generic_aggregate_tree_opening_frontier_2d_v1",
            "generic_weighted_inverse_square_contribution_rows_2d_v1",
            "generic_grouped_vector_sum_rows_2d_v1",
            "generic_weighted_inverse_square_vector_sum_2d_v1",
            "generic_vector_sum_materialization_pressure_2d_v1",
            "generic_aggregate_frontier_weighted_vector_sum_2d_v1",
            "hierarchical aggregate descriptors",
            "vector-valued reductions",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_closeout_records_authors_code_gate_and_claim_boundary(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "https://github.com/vani-nag/OWLRayTracing",
            "BarnesHutRT",
            "2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7",
            "Could NOT find OptiX",
            "missing: OptiX_ROOT_DIR",
            "Disallowed statements",
            "RTDL reproduces the RT-BarnesHut paper",
            "RTDL outperforms the authors' implementation",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_closeout_records_validation_and_next_target(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "Local focused suite",
            "51 tests OK",
            "Pod focused suite",
            "ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex",
            "Torch/CUDA partner-resident fused traversal",
            "OptiX fused traversal",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_benchmark_files_expose_fused_and_cpp_baseline(self) -> None:
        readme_text = README.read_text()
        script_text = SCRIPT.read_text()
        self.assertIn("fused_frontier_force_sum_bucketized_cpu", readme_text)
        self.assertIn("goal2539_barnes_hut_same_contract_cpp_baseline.py", readme_text)
        self.assertIn("fused_frontier_force_sum_bucketized_cpu", script_text)
        self.assertIn("sum_aggregate_frontier_weighted_vectors_2d", script_text)


if __name__ == "__main__":
    unittest.main()
