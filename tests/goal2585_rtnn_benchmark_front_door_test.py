from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rtnn" / "README.md"
BENCH_README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md"
EXAMPLES_README = ROOT / "examples" / "README.md"
CATALOG = ROOT / "docs" / "application_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal2585_rtnn_benchmark_front_door_2026-05-24.md"


def _run_app(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(APP), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal2585RtnnBenchmarkFrontDoorTest(unittest.TestCase):
    def test_scope_records_benchmark_without_native_app_customization(self) -> None:
        payload = _run_app("--mode", "scope")

        self.assertEqual(payload["app"], "rtnn_neighbor_search")
        self.assertEqual(payload["status"], "promoted_benchmark_with_boundary")
        self.assertTrue(payload["claim_boundary"]["benchmark_app"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])
        self.assertFalse(payload["claim_boundary"]["full_rtnn_paper_reproduction"])
        self.assertIn("prepared search-side structures", payload["runtime_design_pressure"])
        self.assertIn("rtnn_ranked_summary_3d", {row["name"] for row in payload["supported_contracts"]})

    def test_ann_cpu_quality_keeps_existing_candidate_contract(self) -> None:
        payload = _run_app("--mode", "ann_cpu_quality", "--copies", "1")

        self.assertEqual(payload["benchmark_app"], "rtnn_neighbor_search")
        self.assertEqual(payload["app"], "ann_candidate_search")
        self.assertEqual(payload["recall_at_1"], 2 / 3)
        self.assertEqual(payload["exact_match_count"], 2)
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertFalse(payload["claim_boundary"]["ann_index_claim_authorized"])

    def test_rtnn_known_results_preserve_same_contract_boundary(self) -> None:
        payload = _run_app("--mode", "rtnn_known_results")

        rows = {row["distribution"]: row for row in payload["rows_65536"]}
        self.assertGreater(rows["uniform"]["cupy_over_rtdl"], 1000.0)
        self.assertGreater(rows["clustered"]["cupy_over_rtdl"], 50.0)
        self.assertGreater(rows["shell"]["cupy_over_rtdl"], 1000.0)
        self.assertFalse(rows["uniform"]["same_contract_with_official_rtnn"])
        self.assertFalse(payload["claim_boundary"]["full_rtnn_paper_reproduction"])
        scale_rows = {row["distribution"]: row for row in payload["rtdl_scale_rows_262144"]}
        self.assertEqual(scale_rows["uniform"]["rtdl_row_count"], 262144)
        self.assertEqual(scale_rows["clustered"]["official_rtnn_returncode"], 1)

    def test_docs_and_catalog_list_rtnn_as_bounded_benchmark(self) -> None:
        readme = README.read_text(encoding="utf-8")
        bench_readme = BENCH_README.read_text(encoding="utf-8")
        examples_readme = EXAMPLES_README.read_text(encoding="utf-8")
        catalog = CATALOG.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("RTNN Neighbor-Search Benchmark", readme)
        self.assertIn("formal front door for the existing RTNN benchmark", readme)
        self.assertIn("not full RTNN paper reproduction", readme)
        self.assertIn("No ANN-specific or RTNN-specific native ABI", readme)
        self.assertIn("rtnn/", bench_readme)
        self.assertIn("RTNN neighbor search", examples_readme)
        self.assertIn("research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py", catalog)
        self.assertIn("Promote the existing RTNN campaign", report)
        self.assertIn("helper submode only", report)
        self.assertIn("not an app-specific engine path", report)


if __name__ == "__main__":
    unittest.main()
