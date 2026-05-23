from pathlib import Path
import json
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2530_barnes_hut_benchmark_app_promotion_2026-05-23.md"
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"
RESEARCH_README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md"
SCRIPT = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "barnes_hut"
    / "rtdl_barnes_hut_benchmark_app.py"
)

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from examples.v2_0.research_benchmarks.barnes_hut import rtdl_barnes_hut_benchmark_app as bench


class Goal2530BarnesHutBenchmarkPromotionTest(unittest.TestCase):
    def test_scope_payload_records_paper_reference_and_blocks_claims(self) -> None:
        payload = bench.run_benchmark("scope")
        metadata = payload["benchmark_metadata"]
        self.assertEqual(metadata["benchmark"], "barnes_hut_ppopp2025_style")
        self.assertEqual(metadata["paper_reference"]["doi"], "10.1145/3710848.3710885")
        self.assertFalse(metadata["paper_reproduction"])
        self.assertFalse(metadata["authors_code_comparison"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["native_engine_app_specific"])
        self.assertIn("hierarchical spatial aggregate descriptors", payload["runtime_pressure"])
        self.assertIn("full RT-BarnesHut paper reproduction", payload["current_non_goals"])

    def test_cpu_reference_mode_preserves_existing_bounded_app_behavior(self) -> None:
        payload = bench.run_benchmark("cpu_reference")
        self.assertEqual(payload["app"], "barnes_hut_force_app")
        self.assertLess(payload["max_relative_error"], 0.01)
        metadata = payload["benchmark_metadata"]
        self.assertEqual(
            metadata["contract"],
            "one_level_candidate_rows_plus_python_opening_rule_force_reference",
        )
        self.assertFalse(metadata["rt_core_accelerated"])
        self.assertIn("not a full RT-BarnesHut paper reproduction", metadata["claim_boundary"])

    def test_node_coverage_oracle_mode_has_same_contract_metadata(self) -> None:
        payload = bench.run_benchmark("node_coverage_cpu_oracle", body_count=16)
        self.assertEqual(payload["body_count"], 16)
        self.assertEqual(payload["benchmark_metadata"]["contract"], "fixed_radius_node_coverage_cpu_oracle")
        self.assertIn("all_bodies_have_node_candidate", payload["node_coverage"])

    def test_cli_scope_mode_outputs_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--mode", "scope"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["benchmark_metadata"]["mode"], "scope")
        self.assertIn("partner force-reference contracts", payload["benchmark_metadata"]["benchmark_scope"])

    def test_docs_register_benchmark_and_boundary(self) -> None:
        for path in (REPORT, README, RESEARCH_README):
            with self.subTest(path=path):
                self.assertTrue(path.exists())
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        research_text = RESEARCH_README.read_text()
        for phrase in [
            "RT-BarnesHut-style reconstruction instrument",
            "not a full RT-BarnesHut paper reproduction",
            "authors-code comparison",
            "native Barnes-Hut ABI",
            "weighted source points + aggregate tree nodes",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("DOI: `10.1145/3710848.3710885`", readme_text)
        self.assertIn("Native Embree/OptiX paths must remain app-name-free", readme_text)
        self.assertIn("`barnes_hut/`", research_text)


if __name__ == "__main__":
    unittest.main()
