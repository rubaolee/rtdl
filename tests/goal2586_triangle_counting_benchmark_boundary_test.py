from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "triangle_counting" / "README.md"
BENCH_README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md"
CATALOG = ROOT / "docs" / "application_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal2586_graph_analytics_benchmark_promotion_2026-05-24.md"
MILESTONE = ROOT / "docs" / "reports" / "goal2587_benchmark_apps_milestone_report_2026-05-24.md"


def _run_app(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(APP), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal2586TriangleCountingBenchmarkBoundaryTest(unittest.TestCase):
    def test_scope_promotes_only_triangle_counting(self) -> None:
        payload = _run_app("--mode", "scope")

        self.assertEqual(payload["app"], "triangle_counting")
        self.assertEqual(payload["benchmark_kind"], "single_contract_graph_benchmark")
        self.assertIn("RT-Graph", payload["paper_reference"]["code"])
        self.assertEqual(payload["paper_reference"]["benchmark_scope"], "triangle_counting_only")
        self.assertEqual(payload["paper_reference"]["reproduction_status"], "contract_oracle_only")
        self.assertTrue(payload["claim_boundary"]["benchmark_app"])
        self.assertTrue(payload["claim_boundary"]["paper_code_intake_complete"])
        self.assertTrue(payload["claim_boundary"]["rt_graph_preprocessing_oracle"])
        self.assertTrue(payload["claim_boundary"]["rt_graph_id_ascending_adapter"])
        self.assertTrue(payload["claim_boundary"]["rt_graph_2a1_generic_rt_mapping"])
        self.assertTrue(payload["claim_boundary"]["rt_graph_1a2_generic_rt_mapping"])
        self.assertFalse(payload["claim_boundary"]["paper_reproduction"])
        self.assertFalse(payload["claim_boundary"]["bfs_in_benchmark"])
        self.assertFalse(payload["claim_boundary"]["visibility_edges_in_benchmark"])
        self.assertEqual(
            {row["name"] for row in payload["supported_contracts"]},
            {"triangle_count"},
        )
        self.assertIn("BFS", payload["excluded_from_benchmark"])
        self.assertIn("visibility_edges", payload["excluded_from_benchmark"])

    def test_run_mode_has_only_triangle_count_contract(self) -> None:
        payload = _run_app(
            "--mode",
            "run",
            "--backend",
            "cpu_python_reference",
            "--copies",
            "2",
            "--output-mode",
            "summary",
        )

        self.assertEqual(payload["benchmark_app"], "triangle_counting")
        self.assertEqual(payload["contract"], "triangle_count_only")
        self.assertEqual(payload["triangle_count"], 2)
        self.assertEqual(payload["touched_vertex_count"], 6)
        self.assertEqual(payload["excluded_operations"], ["bfs", "visibility_edges"])
        self.assertNotIn("bfs", payload)
        self.assertNotIn("visibility_edges", payload)
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])

    def test_docs_exclude_broad_graph_benchmark_wording(self) -> None:
        readme = README.read_text(encoding="utf-8")
        bench_readme = BENCH_README.read_text(encoding="utf-8")
        catalog = CATALOG.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        milestone = MILESTONE.read_text(encoding="utf-8")

        self.assertIn("Triangle Counting Benchmark", readme)
        self.assertIn("RT-Graph", readme)
        self.assertIn("SIGMETRICS 2025", readme)
        self.assertIn("intentionally not part", readme)
        self.assertIn("triangle_counting/", bench_readme)
        self.assertIn("RT-Graph", bench_readme)
        self.assertNotIn("graph_analytics/", bench_readme)
        self.assertIn("learner/demo graph app", catalog)
        self.assertIn("RT-Graph-style triangle counting only", catalog)
        self.assertIn("Triangle counting", report)
        self.assertIn("RT-Graph", report)
        self.assertIn("BFS and visibility-edge modes are learner/demo/example surfaces", report)
        self.assertIn("Triangle counting", milestone)
        self.assertIn("SIGMETRICS 2025", milestone)
        self.assertNotIn("Graph analytics | Promoted as bounded", milestone)


if __name__ == "__main__":
    unittest.main()
